from sys import stderr
from base64 import b64decode
from datetime import datetime
from os import stat, makedirs
from os.path import exists, dirname
from requests.api import get
from subprocess import run

from ansible.parsing.vault import VaultLib, VaultSecret
import boto3

VAULT_ID = 'default'


def now():
    return datetime.now()


def log(msg):
    stderr.write(f'[{now()}] {msg}\n')


def publish_sentry_release(
    token,
    service_name,
    environment,
    project_name,
    tag_name,
    release_ref,
    release_url,
):
    def sentry_releases_cmd(args):
        # install sentry-cli via homebrew
        cmd = ['/usr/local/bin/sentry-cli', 'releases']
        cmd.extend(args.split(' '))
        from pprint import pprint

        pprint(cmd)
        return cmd

    env = {
        'SENTRY_AUTH_TOKEN': token,
        'SENTRY_ORG': service_name,
    }

    log(f'Initiating new release: {tag_name}')
    run(
        sentry_releases_cmd(f'new --project {project_name} '
                            f'--url {release_url} {tag_name}'), env=env
    )
    log(f'Linking commit: {release_ref}')
    run(sentry_releases_cmd(f'set-commits --commit {release_ref} {tag_name}'),
        env=env)
    log('Finalizing release.')
    run(sentry_releases_cmd(f'finalize {tag_name}'), env=env)
    log(f'Deploying new release to environment {environment}.')
    run(
        sentry_releases_cmd(
            f'deploys {tag_name} new '
            f'--name {project_name}-{environment}/{tag_name} '
            f'--env {environment}'
        ),
        env=env,
    )


def get_tag_commit(token, repo, tag):
    h = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'token  {token}'
        }
    url = f'https://api.github.com/repos/{repo}/git/matching-refs/tags/{tag}'
    r = get(url, headers=h)
    if r.status_code != 200:
        log(f'[ERROR] {url} returned {r.status_code}\n')
        raise Exception(f'Unable to get commit for {repo}@{tag}')
    sha = r.json()[0]['object']['sha']
    log(f'[INFO] {tag} {sha}')
    return sha


def download_github_release(token, repo, version, dest,
                            content_type='application/zip'):
    if exists(dest) and stat(dest).st_size > 0:
        log(f'[WARN] Archive already downloaded.'
            f'Remove [{dest}] to redownload.')
    else:
        # Update Authorization to use 'Bearer' for Personal Access Tokens
        # curl -L \
        # -H "Accept: application/vnd.github+json" \
        # -H "Authorization: Bearer ${GITHUB_TOKEN}" \
        # -H "X-GitHub-Api-Version: 2022-11-28" \
        # https://api.github.com/repos/ebridges/elektrum-processor/releases/tags/v1.2.1
        h = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'Bearer {token}',
            'X-GitHub-Api-Version': '2022-11-28',
        }
        download_url = (f'https://api.github.com/repos/{repo}/releases/'
                        f'tags/v{version}')
        log(f'[INFO] headers: {h}')
        log(f'[INFO] url: {download_url}')
        r = get(download_url, headers=h)
        if r.status_code != 200:
            log(f'[ERROR] {download_url} returned {r.status_code}\n')
            return False

        def lookup_url(content):
            from pprint import pprint

            pprint(content)
            for asset in content['assets']:
                if asset['content_type'] == content_type:
                    return asset['url']

        asset_url = lookup_url(r.json())
        if not asset_url:
            log(f'[ERROR] No matching asset found for {content_type}.')
            return False

        # Update Accept header to download the actual asset file
        h['Accept'] = 'application/octet-stream'
        log(f'[INFO] Downloading archive from [{asset_url}].')
        download_from_url(asset_url, dest, headers=h)
        log(f'[INFO] Archive downloaded locally to [{dest}].')

    # Return True if the file was downloaded successfully
    return True


def download_from_url(url, file, headers={}, allow_redirects=True, stream=True,
                      chunk_size=256):
    ensure_dir(file)
    r = get(url, headers=headers, allow_redirects=allow_redirects,
            stream=stream)
    with open(file, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)
    return file


def ensure_dir(file):
    dir = dirname(file)
    if not exists(dir):
        makedirs(dir)


def decrypt_value(passwd, encrypted_val):
    secret = VaultSecret(_bytes=passwd.encode('utf-8'))
    vault = VaultLib(secrets=[(VAULT_ID, secret)])
    decrypted_bytes = vault.decrypt(encrypted_val)
    return decrypted_bytes.decode('utf-8')


def get_encrypted_field(vault_file, key):
    '''
    Reads an encrypted value under `key` from the given vault file.
    This is a workaround as `pyyaml` had issues reading encrypted
    entries from vault files.
    '''
    with open(vault_file) as fp:
        lines = list(fp)
        cnt = 0
        code = ''
        for line_ in lines:
            line = line_.strip()
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
        FunctionName=lambda_name, InvocationType='RequestResponse',
        LogType='Tail', Payload=payload
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
