#!/usr/bin/env python3

from sys import argv
from toml import load, dump
from argparse import ArgumentParser


def main(argv):
  parser = ArgumentParser(prog=argv[0])
  parser.add_argument('-v', '--version', required=True, help='New version for the project.')
  parser.add_argument('-f', '--file', required=True, default='pyproject.toml', help='Project file.')
  args = parser.parse_args()

  doc = load(args.file)
  doc['tool']['poetry']['version'] = args.version
  with open(args.file, 'w') as f:
    dump(doc, f)
  print('Project updated to version: %s' % args.version)

if __name__ == '__main__':
    main(argv)
