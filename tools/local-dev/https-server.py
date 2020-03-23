from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl
import os
import sys

# generate self signed certificate:
#   `openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes`
#
# in chrome allow self-signed certs on localhost
#   `chrome://flags/#allow-insecure-localhost`

certfile = os.path.join(os.getcwd(), 'server.pem')

if len(sys.argv) > 1:
    web_dir = os.path.join(os.getcwd(), sys.argv[1])
    os.chdir(web_dir)

httpd = HTTPServer(('localhost', 9443), SimpleHTTPRequestHandler)

httpd.socket = ssl.wrap_socket(httpd.socket, certfile=certfile, server_side=True)

httpd.serve_forever()
