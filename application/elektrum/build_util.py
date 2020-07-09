from base64 import b64decode
from os.path import exists
from requests.api import get

from ansible.parsing.vault import VaultLib, VaultSecret
import boto3

VAULT_ID = 'default'

ELEKTRUM_PROCESSOR_VERSION = '1.0.6'


def download_github_release(token, project, version, dest):
    if not exists(dest):
        h = {'Accept': 'application/vnd.github.v3+json', 'Authorization': f'token  {token}'}
        download_url = f'https://api.github.com/repos/ebridges/{project}/releases/tags/v{version}'
        r = get(download_url, headers=h)
        content = r.json()
        asset_url = content['assets'][0]['url']

        h['Accept'] = 'application/octet-stream'
        print(f'Downloading from {asset_url}')
        r = get(asset_url, headers=h, allow_redirects=True, stream=True)
        chunk_size = 256
        with open(dest, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=chunk_size):
                fd.write(chunk)
        print(f'Release archive successfully downloaded to {dest}')
    else:
        print(f'Release archive already downloaded locally.  Remove {dest} to redownload.')
    return True


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


if __name__ == '__main__':

    def test_decrypt_value():
        passwd = slurp(f'network/environments/development-vault-password.txt')
        encrypted_value = f'''$ANSIBLE_VAULT;1.1;AES256;{VAULT_ID}
    61356435653662323936333961663861366365336166663038373936373030666364663939366330
    6530633932666235663035303831613536336637313064390a656337323437303364366166353536
    36613637363633383432643862343830616663333732616436643930643561356266356162313563
    3534393635616230370a393162363832656531353465353733323163616533353766646133373366
    3233'''
        expected_value = 'test_value'
        actual_vale = decrypt_value(passwd, encrypted_value)
        assert expected_value == actual_vale

    test_decrypt_value()
