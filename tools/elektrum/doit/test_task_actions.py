from elektrum.doit.util import slurp, decrypt_value, VAULT_ID


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