#!/usr/bin/env python

import subprocess
import os
import signal
from threading import Thread
import time
import requests
import sys

process=None

urls_to_test = [
  {'url': 'http://localhost/status/ok', 'header': 'X-Elektrum-Now'},
  {'url': 'http://localhost/static/img/logo.png'},
]


def run_tests():
  has_errors = False
  for url_info in urls_to_test:
    url = url_info['url']
    try:
      header_val = test_url(url, url_info.get('header'))
    except AssertionError as e:
      print('[FAIL]: %s [%s]' % (url,e))
      has_errors=True
    else:
      if header_val:
        print('[OK]: %s (%s)' % (url, header_val))
      else:
        print('[OK]: %s' % url)
  return has_errors


def test_url(url, header=None):
  header_val = None
  try:
    r = requests.head(url, allow_redirects=True)
    if header:
      if header in r.headers:
        header_val = r.headers[header]
      else:
        header_val = 'Header [%s] not found' % header
    if r.status_code >= 400:
      raise AssertionError('status code %d' % r.status_code)
    return header_val
  except requests.ConnectionError as e:
    raise AssertionError('cannot connect to container: %s' % e)


def main():
  s = Thread(name='http-server', target=start_docker_compose)
  s.start()
  time.sleep(10)
  result = 0
  message = 'Test Completed'

  if run_tests():
    message += ' - ERROR'
    result = 1
  else:
    message += ' - OK'

  os.killpg(os.getpgid(process.pid), signal.SIGTERM)
  time.sleep(5)
  s.join()

  print(message)
  return result

def start_docker_compose():
  global process
  process = subprocess.Popen(args='docker-compose up', stdout=subprocess.PIPE,
                       shell=True, preexec_fn=os.setsid) 

if __name__ == "__main__":
    sys.exit(main())
