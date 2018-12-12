import subprocess
import os
import signal
from threading import Thread
import time
import requests
import sys

process=None

def run_test():
  try:
      print("testing localhost")
      r = requests.head("http://localhost/status/ok")
      print("response %s" % r.status_code)
      if r.status_code < 400:
        print("OK")
      else:
        raise AssertionError("status not okay")
  except requests.ConnectionError:
    raise AssertionError("container does not work")


def main():
  s = Thread(name='http-server', target=start_docker_compose)
  s.start()
  time.sleep(5)
  result = 0
  message = 'Test Completed'
  try:
    run_test()
    message += ' - OK'
  except AssertionError as e:
    message += ' - ERROR: %s' % e
    result = 1
  finally:
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
