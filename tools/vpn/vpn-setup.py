from argparse import ArgumentParser
from boto3 import client as ec2_client
from datetime import datetime
from logging import basicConfig, DEBUG, INFO, debug, info
from re import findall
from sys import argv
from os.path import dirname, realpath
from dotenv import load_dotenv
from os import environ
from subprocess import run, PIPE, DEVNULL

dir_path = dirname(realpath(__file__))
BASE_DIR = realpath(f'{dir_path}/../..')
DEFAULT_CLIENT_CIDR = '192.168.0.0/16'


def client_endpoint_name(service_name, operating_env):
    return '%s-%s-vpn' % (service_name, operating_env)


def lookup_endpoint_id(info, name):
    for ep in info['ClientVpnEndpoints']:
        for tag in ep['Tags']:
            if tag.get('Key') == 'Name' and tag.get('Value') == name:
                return ep['ClientVpnEndpointId']
    return None


def find_endpoint_by_name(client, endpoint_name):
    response = client.describe_client_vpn_endpoints(MaxResults=5, DryRun=False)

    debug(response)

    return lookup_endpoint_id(response, endpoint_name)


def delete_endpoint(service_name, operating_env):
    client = ec2_client('ec2')

    endpoint_name = client_endpoint_name(service_name, operating_env)

    endpoint_id = find_endpoint_by_name(client, endpoint_name)

    if not endpoint_id:
        raise Exception(f'Unable to find endpoint named {endpoint_name}')

    response = client.describe_client_vpn_target_networks(
        ClientVpnEndpointId=endpoint_id, MaxResults=5, DryRun=False
    )
    debug(response)

    association_ids = []
    for nw in response['ClientVpnTargetNetworks']:
        if nw['ClientVpnEndpointId'] == endpoint_id:
            association_ids.append(nw['AssociationId'])

    for association_id in association_ids:
        response = client.disassociate_client_vpn_target_network(
            ClientVpnEndpointId=endpoint_id, AssociationId=association_id, DryRun=False
        )
        debug(response)

    response = client.delete_client_vpn_endpoint(ClientVpnEndpointId=endpoint_id, DryRun=False)
    debug(response)


def create_endpoint(
    service_name,
    operating_env,
    vpc_id,
    client_cidr,
    server_cert,
    client_cert,
    security_groups,
    public_subnets,
):
    client = ec2_client('ec2')

    endpoint_name = client_endpoint_name(service_name, operating_env)

    endpoint_id = find_endpoint_by_name(client, endpoint_name)

    if not endpoint_id:
        authn_options = [
            {
                'Type': 'certificate-authentication',
                'MutualAuthentication': {
                    'ClientRootCertificateChainArn': client_cert  ## TODO this should be the root certificate chain ARN!!
                },
            }
        ]

        connection_log = {'Enabled': False}
        description = '%s-%s-vpn: Created by %s on %s' % (
            service_name,
            operating_env,
            argv[0],
            str(datetime.now()),
        )
        split_tunnel = True
        tags = [
            {
                'ResourceType': 'client-vpn-endpoint',
                'Tags': [
                    {'Key': 'Name', 'Value': endpoint_name},
                    {'Key': 'Operating-Env', 'Value': operating_env},
                ],
            }
        ]
        security_group_ids = [c.strip() for c in security_groups.split(',') if not c.isspace()]
        public_subnet_ids = [c.strip() for c in public_subnets.split(',') if not c.isspace()]

        response = client.create_client_vpn_endpoint(
            ClientCidrBlock=client_cidr,
            ServerCertificateArn=server_cert,
            AuthenticationOptions=authn_options,
            ConnectionLogOptions=connection_log,
            DnsServers=[],
            TransportProtocol='udp',
            Description=description,
            SplitTunnel=split_tunnel,
            VpnPort=443,
            DryRun=False,
            TagSpecifications=tags,
            SecurityGroupIds=security_group_ids,
            VpcId=vpc_id,
        )

        endpoint_id = response['ClientVpnEndpointId']
        status = response['Status']['Code']
        info(f'Created VPN Client Endpoint [id: {endpoint_id}]. Status is {status}')

    for subnet_id in public_subnet_ids:
        response = client.associate_client_vpn_target_network(
            ClientVpnEndpointId=endpoint_id, SubnetId=subnet_id, DryRun=False
        )
        info(f'Associated {subnet_id} with {endpoint_id}')

    destination_network = '10.0.0.0/8'  ## TODO parameterize this
    response = client.authorize_client_vpn_ingress(
        ClientVpnEndpointId=endpoint_id,
        TargetNetworkCidr=destination_network,
        AuthorizeAllGroups=True,
        DryRun=False,
    )
    status = response['Status']['Code']
    info(
        f'Authorized Client Ingress for endpoint [id: {endpoint_id}] to {destination_network}. Status is {status}'
    )


def configure_logging(verbose):
    if verbose:
        level = DEBUG
    else:
        level = INFO

    basicConfig(
        format='[%(asctime)s][%(levelname)s] %(message)s', datefmt='%Y/%m/%d %H:%M:%S', level=level
    )


def shell_cmd(env, key):
    cmd = f'yq read {BASE_DIR}/network/group_vars/{env}.yml "{key}"'
    cmd += ' | '
    cmd += f'ansible-vault decrypt --vault-password-file={BASE_DIR}/network/environments/{env}-vault-password.txt'
    return cmd


def exec_cmd(cmd):
    result = run(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=DEVNULL)
    return result.stdout.decode('utf-8')


def load_env(environment):
    env_file = f'{BASE_DIR}/etc/env/{environment}.env'
    load_dotenv(env_file)
    access_key_cmd = shell_cmd(environment, 'aws_access_key')
    access_key = exec_cmd(access_key_cmd)
    environ['AWS_ACCESS_KEY_ID'] = access_key
    environ['AWS_SECRET_ACCESS_KEY'] = exec_cmd(shell_cmd(environment, 'aws_secret_key'))


def main(argv):
    parser = ArgumentParser(prog=argv[0])
    parser.add_argument('-v', '--verbose', default=False, action='store_true')
    parser.add_argument(
        '-e',
        '--env',
        required=True,
        choices={'development', 'staging', 'production'},
        help='Operating environment. [development|staging|production]',
    )
    sp = parser.add_subparsers(
        title='Create or Delete a Client VPN Endpoint',
        description='Creates or deletes a client VPN endpoint in the given operating environment.',
        dest='action',
    )
    sp_start = sp.add_parser(
        'create', help='Creates a client VPN endpoint in the given operating environment.'
    )
    sp_start.add_argument(
        '-c', '--client-cidr', default=DEFAULT_CLIENT_CIDR, help='Client IP Address Range.'
    )
    sp_stop = sp.add_parser(
        'delete', help='Deletes a client VPN endpoint in the given operating environment.'
    )

    args = parser.parse_args()

    configure_logging(args.verbose)
    load_env(args.env)

    debug(args)
    if args.action == 'delete':
        service_name = environ['SERVICE_NAME']
        operating_env = environ['ENVIRONMENT']

        delete_endpoint(service_name, operating_env)

    if args.action == 'create':
        service_name = environ['SERVICE_NAME']
        operating_env = environ['ENVIRONMENT']
        vpc_id = environ['VPC_ID']
        server_cert = environ['VPN_SERVER_CERTIFICATE_ARN']
        client_cidr = args.client_cidr
        client_cert = environ['VPN_CLIENT_CA_CERTIFICATE_ARN']
        public_subnets = environ['VPC_PUBLIC_SUBNET_IDS']
        security_groups = environ['VPC_NAT_SECURITY_GROUP_IDS']

        info('Creating a new client endpoint with parameters:')
        info(f'    service_name: {service_name}')
        info(f'    operating_env: {operating_env}')
        info(f'    vpc_id: {vpc_id}')
        info(f'    server_cert: {server_cert}')
        info(f'    client_cert: {client_cert}')
        info(f'    client_cidr: {client_cidr}')
        info(f'    public_subnets: {public_subnets}')
        info(f'    security_groups: {security_groups}')

        create_endpoint(
            service_name,
            operating_env,
            vpc_id,
            client_cidr,
            server_cert,
            client_cert,
            security_groups,
            public_subnets,
        )


if __name__ == '__main__':
    main(argv)
