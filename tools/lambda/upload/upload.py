import requests
from sys import argv


def upload_photo(photo, url):
    files = {'file': open(photo, 'rb')}
    response = requests.put(url, files=files)
    print(
        'RESPONSE: {status_code}\n{headers}\n\n{body}'.format(
            status_code=response.status_code,
            headers='\n'.join('{}: {}'.format(k, v) for k, v in response.headers.items()),
            body=response.content,
        )
    )


if __name__ == '__main__':
    photo = ''
    url = ''
    upload_photo(photo, url)
