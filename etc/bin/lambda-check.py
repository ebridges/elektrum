#!/usr/bin/env python3

from sys import argv
from argparse import ArgumentParser
from logging import debug, INFO, DEBUG, basicConfig


def app(args):
    pass


def main(argv):
    parser = ArgumentParser(prog=argv[0])
    parser.add_argument(
        '-v', '--version_file', required=False, default='version.txt', help='Version file.'
    )
    parser.add_argument(
        '-d',
        '--dev',
        required=False,
        action='store_true',
        help='Dev variant of the version number.',
    )
    parser.add_argument('--verbose')

    group = parser.add_argument_group('incrementing version')
    group.add_argument(
        '-n',
        '--next',
        required=False,
        action='store_true',
        default=False,
        help='Increment the version',
    )
    group.add_argument(
        '-p',
        '--part',
        required=False,
        action='store',
        type=int,
        default=1,
        help='Which part of the version to increment.',
    )

    args = parser.parse_args()

    if args.verbose:
        basicConfig(level=DEBUG)

    app(args)


if __name__ == '__main__':
    main(argv)
