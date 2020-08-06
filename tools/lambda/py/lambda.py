from logging import debug, info, error
from urllib.request import urlopen


def handler(event, context):
    url = 'https://jsonplaceholder.typicode.com/todos/1'
    r = urlopen(url)
    if r.status != 200:
        error(f'[ERROR] {url} returned {r.status}\n')
        raise Exception(f'[ERROR] {url} returned {r.status}')
    response = r.read().decode('utf-8')
    info(response)
