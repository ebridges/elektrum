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
  'http://localhost/status/ok',
  'http://localhost/static/img/logo.png',
]


def run_tests():
  has_errors = False
  for url in urls_to_test:
    try:
      test_url(url)
    except AssertionError as e:
      print('[FAIL]: %s [%s]' % (url,e))
      has_errors=True
    else:
      print('[OK]: %s' % url)
  return has_errors


def test_url(url):
  try:
    r = requests.head(url)
    if r.status_code >= 400:
      raise AssertionError('status code %d' % r.status_code)
  except requests.ConnectionError as e:
    raise AssertionError('cannot connect to container: %s' % e)


def main():
  s = Thread(name='http-server', target=start_docker_compose)
  s.start()
  time.sleep(5)
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
