from http.server import HTTPServer, SimpleHTTPRequestHandler
from ssl import wrap_socket
from os import chdir
from sys import argv
from pathlib import Path
from tempfile import NamedTemporaryFile
from subprocess import run, DEVNULL

# generate self signed certificate:
#   `openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes`
#
# in chrome allow self-signed certs on localhost
#   `chrome://flags/#allow-insecure-localhost`

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 9443
DEFAULT_EXPIRY_DAYS = '365'


def generate_pem(pemfile):
    subject = f'/C=US/ST=NY/L=New York/O=Elektrum/OU=Engineering/CN={DEFAULT_HOST}'
    command = [
        'openssl',
        'req',
        '-new',
        '-x509',
        '-keyout',
        pemfile,
        '-out',
        pemfile,
        '-subj',
        subject,
        '-days',
        DEFAULT_EXPIRY_DAYS,
        '-nodes',
    ]
    result = run(command, stdout=DEVNULL, stderr=DEVNULL)
    result.check_returncode()


if len(argv) > 1:
    chdir(argv[1])

with NamedTemporaryFile(suffix='.pem') as tmp:
    generate_pem(tmp.name)
    print(
        f'Starting HTTPS server at https://{DEFAULT_HOST}:{DEFAULT_PORT} using cert at {tmp.name}'
    )
    httpd = HTTPServer((DEFAULT_HOST, DEFAULT_PORT), SimpleHTTPRequestHandler)
    httpd.socket = wrap_socket(httpd.socket, certfile=tmp.name, server_side=True)
    httpd.serve_forever()
