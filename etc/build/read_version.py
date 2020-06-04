#!/usr/bin/env python3

from sys import argv
from argparse import ArgumentParser
from logging import debug, INFO, DEBUG, basicConfig
import unittest

from etc.build.util import slurp

basicConfig(level=INFO)


DEV_EXTENSION = 'dev0'


def curr_version(version):
    debug(f'curr_version({version})')
    parts = version.split('.')
    return '.'.join(parts[0:2])


def curr_dev_version(version):
    debug(f'curr_dev_version({version})')
    if not version.endswith(DEV_EXTENSION):
        version = f'{version}.{DEV_EXTENSION}'
    return version


def next_version(version, idx=1):
    debug(f'next_version({version}, {idx})')
    parts = version.split('.')
    parts[idx] = str(int(parts[idx]) + 1)
    return '.'.join(parts[0:2])


def next_dev_version(version, idx=1):
    debug(f'next_dev_version({version}, {idx})')
    if not version.endswith(DEV_EXTENSION):
        version = f'{version}.{DEV_EXTENSION}'
    parts = version.split('.')
    debug(parts)
    debug(idx)
    parts[idx] = str(int(parts[idx]) + 1)
    return '.'.join(parts)


def read(version_file, dev=False, next=False, part=1):
    version = slurp(version_file)

    if dev and not next:
        return curr_dev_version(version)

    if dev and next:
        return next_dev_version(version, part)

    if not dev and not next:
        return curr_version(version)

    if not dev and next:
        return next_version(version, part)


def read(version, args):
    return read_version(version, args['dev'], args['next'], args['part'])


def read_from_file(version_file, dev=False, next=False, part=1):
    version = slurp(version_file)
    return read_version(version, dev, next, part)


def read_version(version, dev, next, part):
    if dev and not next:
        return curr_dev_version(version)

    if dev and next:
        return next_dev_version(version, part)

    if not dev and not next:
        return curr_version(version)

    if not dev and next:
        return next_version(version, part)


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

    version = read_from_file(args.version_file, args['dev'], args['next'], args['part'])

    print(version)


# To run tests:
#    `python -m unittest version_info.py`
class TestStringMethods(unittest.TestCase):
    def test_curr_dev(self):
        version = '0.36.dev0'
        args = {'dev': True, 'next': False, 'part': 1}
        expected = '0.36.dev0'
        actual = read(version, args)
        self.assertEqual(expected, actual)

    def test_next_dev(self):
        version = '0.36.dev0'
        args = {'dev': True, 'next': True, 'part': 1}
        expected = '0.37.dev0'
        actual = read(version, args)
        self.assertEqual(expected, actual)

    def text_curr(self):
        version = '0.36.dev0'
        args = {'version': '0.36.dev0', 'dev': False, 'next': False, 'part': 1}
        expected = '0.36'
        actual = read(version, args)
        self.assertEqual(expected, actual)

    def test_next(self):
        version = '0.36.dev0'
        args = {'version': '0.36.dev0', 'dev': False, 'next': True, 'part': 1}
        expected = '0.37'
        actual = read(version, args)
        self.assertEqual(expected, actual)

    def test_curr_dev_firstpart(self):
        version = '0.36.dev0'
        args = {'version': '0.36.dev0', 'dev': True, 'next': False, 'part': 0}
        expected = '0.36.dev0'
        actual = read(version, args)
        self.assertEqual(expected, actual)

    def test_next_dev_firstpart(self):
        version = '0.36.dev0'
        args = {'version': '0.36.dev0', 'dev': True, 'next': True, 'part': 0}
        expected = '1.36.dev0'
        actual = read(version, args)
        self.assertEqual(expected, actual)

    def text_curr_firstpart(self):
        version = '0.36.dev0'
        args = {'dev': False, 'next': False, 'part': 0}
        expected = '0.36'
        actual = read(version, args)
        self.assertEqual(expected, actual)

    def test_next_firstpart(self):
        version = '0.36.dev0'
        args = {'dev': False, 'next': True, 'part': 0}
        expected = '1.36'
        actual = read(version, args)
        self.assertEqual(expected, actual)

    def test_curr_dev_nondevversion(self):
        version = '0.36'
        args = {'dev': True, 'next': False, 'part': 1}
        expected = '0.36.dev0'
        actual = read(version, args)
        self.assertEqual(expected, actual)

    def test_next_dev_nondevversion(self):
        version = '0.36'
        args = {'dev': True, 'next': True, 'part': 1}
        expected = '0.37.dev0'
        actual = read(version, args)
        self.assertEqual(expected, actual)

    def text_curr_nondevversion(self):
        version = '0.36'
        args = {'dev': False, 'next': False, 'part': 1}
        expected = '0.36'
        actual = read(version, args)
        self.assertEqual(expected, actual)

    def test_next_nondevversion(self):
        version = '0.36'
        args = {'dev': False, 'next': True, 'part': 1}
        expected = '0.37'
        actual = read(version, args)
        self.assertEqual(expected, actual)

    def test_curr_dev_firstpart_nondevversion(self):
        version = '0.36'
        args = {'dev': True, 'next': False, 'part': 0}
        expected = '0.36.dev0'
        actual = read(version, args)
        self.assertEqual(expected, actual)

    def test_next_dev_firstpart_nondevversion(self):
        version = '0.36'
        args = {'dev': True, 'next': True, 'part': 0}
        expected = '1.36.dev0'
        actual = read(version, args)
        self.assertEqual(expected, actual)

    def text_curr_firstpart_nondevversion(self):
        version = '0.36'
        args = {'dev': False, 'next': False, 'part': 0}
        expected = '0.36'
        actual = read(version, args)
        self.assertEqual(expected, actual)

    def test_next_firstpart_nondevversion(self):
        version = '0.36'
        args = {'dev': False, 'next': True, 'part': 0}
        expected = '1.36'
        actual = read(version, args)
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    main(argv)
