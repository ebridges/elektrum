from base64 import b64decode

from ansible.parsing.vault import VaultLib, VaultSecret
import boto3

VAULT_ID = 'default'


def decrypt_value(passwd, encrypted_val):
    secret = VaultSecret(_bytes=passwd.encode('utf-8'))
    vault = VaultLib(secrets=[(VAULT_ID, secret)])
    decrypted_bytes = vault.decrypt(encrypted_val)
    return decrypted_bytes.decode('utf-8')


def get_encrypted_field(vault_file, key):
    '''
    Reads an encrypted value under `key` from the given vault file.
    This is a workaround as `pyyaml` had issues reading encrypted entries from vault files.
    '''
    with open(vault_file) as fp:
        lines = list(fp)
        cnt = 0
        code = ''
        for l in lines:
            line = l.strip()
            if line.startswith(key):
                cnt = cnt + 1
                c = lines[cnt]
                first = True
                while c.strip():
                    code = code + c.strip()
                    if first:
                        first = False
                        code = code + f';{VAULT_ID}\r\n'
                    cnt = cnt + 1
                    c = lines[cnt]
                return code
            cnt = cnt + 1


def slurp(file):
    with open(file) as f:
        v = f.readline()
        return v.strip()


def invoke(lambda_name, payload):
    client = boto3.client('lambda')
    res = client.invoke(
        FunctionName=lambda_name, InvocationType='RequestResponse', LogType='Tail', Payload=payload
    )
    return (
        int(res['ResponseMetadata']['HTTPStatusCode']),
        b64decode(res['LogResult']).decode('utf-8'),
    )
