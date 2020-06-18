#!/usr/bin/env python3

from sys import argv, stdout, exit
from pprint import pprint
from argparse import ArgumentParser

from toml import load

DEFAULT_EXCLUDED = [
    'ansible',
    'boto3',
    'botocore',
    's3transfer',
    'jmsepath',
    'docutils',
    'pywin32',
    'pypiwin32',
]


def parse_project_file(file, include_dev_deps, excluded):
    doc = load(file)
    categories = ['main']
    if include_dev_deps:
        categories.append('dev')

    # pprint(doc)
    deps = {}
    excludes = excluded.split(',')
    for dep in doc['package']:
        name = dep['name']
        if dep['category'] in categories and name not in excludes:
            deps[name] = [dep['version']]
            if 'marker' in dep:
                deps[name].append(dep['marker'])
            if 'python-versions' in dep and dep['python-versions'] != '*':
                pv = [x.strip() for x in dep['python-versions'].split(',')]
                pvs = ['python_version {0}'.format(i) for i in pv]
                pvpv = ' or '.join(pvs)
                deps[name].append(pvpv)

    return deps


def app(project_file, include_dev_deps, excluded, outfile):
    deps = parse_project_file(project_file, include_dev_deps, excluded)

    if outfile:
        out = open(outfile, 'w')
    else:
        out = stdout

    for dep in deps:
        print('%s==%s' % (dep, '; '.join(deps[dep])), file=out)

    if outfile:
        out.close()


def main(args):
    parser = ArgumentParser(prog=argv[0])
    parser.add_argument('-f', '--file', required=True, help='Either pyproject.toml or poetry.lock')
    parser.add_argument(
        '-d',
        '--dev-deps',
        default=False,
        const=True,
        nargs='?',
        type=bool,
        help='Whether to include development dependencies.',
    )
    parser.add_argument(
        '-x',
        '--exclude',
        default=','.join(DEFAULT_EXCLUDED),
        const=','.join(DEFAULT_EXCLUDED),
        nargs='?',
        help='Whether to include development dependencies.',
    )
    parser.add_argument('-o', '--output', required=False, help='Output location, default is stdout')
    args = parser.parse_args()

    app(args.file, args.dev_deps, args.exclude, args.output)


if __name__ == '__main__':
    main(argv)
