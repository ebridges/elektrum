#!/usr/bin/env python3

from sys import argv, stderr, exit
from toml import load
from pprint import pprint

EXCLUDED = ['ansible', 'boto3', 'botocore', 's3transfer', 'jmsepath', 'docutils']


def parse_project_file(file):
    doc = load(file)
    # pprint(doc)
    deps = {}
    for dep in doc['package']:
        name = dep['name']
        if dep['category'] == 'main' and name not in EXCLUDED:
            deps[name] = dep['version']
    return deps


def app(project_file):
    deps = parse_project_file(project_file)
    for dep in deps:
        print('%s==%s' % (dep, deps[dep]))


def main(args):
    if len(args) != 2:
        print('Usage: poetry2pip.py [path to pyproject.toml]', file=stderr)
        exit(1)
    app(args[1])


if __name__ == '__main__':
    main(argv)
