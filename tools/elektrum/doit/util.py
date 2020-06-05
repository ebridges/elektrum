import hashlib
from ansible.parsing.vault import VaultLib, VaultSecret

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


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
