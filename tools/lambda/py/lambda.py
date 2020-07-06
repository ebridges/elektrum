from botocore.vendored import requests


def handler(event, context):
    print('request began -- getting from https://reqres.in/api/users/2')
    response = requests.get('https://reqres.in/api/users/2')
    print(response.json())
