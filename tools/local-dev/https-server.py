from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl
import os
import sys

if len(sys.argv) > 1:
    web_dir = os.path.join(os.path.dirname(__file__), sys.argv[1])
    os.chdir(web_dir)

httpd = HTTPServer(('localhost', 9443), SimpleHTTPRequestHandler)

httpd.socket = ssl.wrap_socket(
    httpd.socket,
    keyfile='/Users/ebridges/Library/Caches/pypoetry/virtualenvs/elektrum-PlTQOJ1Z-py3.7/lib/python3.7/site-packages/sslserver/certs/development.key',
    certfile='/Users/ebridges/Library/Caches/pypoetry/virtualenvs/elektrum-PlTQOJ1Z-py3.7/lib/python3.7/site-packages/sslserver/certs/development.crt',
    server_side=True,
)

httpd.serve_forever()
