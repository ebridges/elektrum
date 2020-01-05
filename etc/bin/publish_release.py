#!/usr/bin/env python3

from os import environ
from sys import argv
from argparse import ArgumentParser
from logging import debug, info, INFO, DEBUG, basicConfig
from datetime import datetime
import re
import requests
import json


def publish(payload):
    info('Publishing payload: %s' % json.dumps(payload))
    post_url = 'https://api.github.com/repos/ebridges/elektrum/releases'
    auth_token = environ.get('GITHUB_OAUTH_TOKEN')  # https://github.com/settings/tokens
    headers = {'Authorization': f'token {auth_token}'}
    r = requests.post(post_url, data=json.dumps(payload), headers=headers)
    if r.status_code > 299:
        return 'ERROR: publishing new release: %s' % r.text
    else:
        return 'SUCCESS: publishing release.'


def get_changelog_entry(changelog, version):
    info(f'getting changelog for {version} from {changelog}')
    date = None
    changes = []
    with open(changelog) as c:
        for line in c:
            line = line.strip().lower()
            debug(f'line: {line}')
            if line.startswith('##') and 'unreleased' not in line:
                if f' {version} ' in line:
                    debug(f'    found {version} in {line}')
                    m = re.search(r'([0-9]{4}-[0-9]{2}-[0-9]{2})', line)
                    date = datetime.strptime(m.group(1), '%Y-%m-%d')
                    for change_line in c:
                        change_line = change_line.strip()
                        debug(f'        change_line: [{change_line}]')
                        if '##' in change_line:
                            break
                        if change_line:
                            debug(f'found a change: {change_line}')
                            changes.append(change_line)
            else:
                debug(f'skipping line: {line}')
    return date, changes


def format_description(info):
    date = datetime.strftime(info[0], '%B %d, %Y')
    return '*%s*\n\n%s' % (date, '\n'.join(info[1]))


def app(args):
    info(f'publishing release version {args.version}')
    change_info = get_changelog_entry(args.changelog, args.version)
    description = format_description(change_info)
    payload = {'tag_name': args.version, 'name': args.release, 'body': description}
    if args.dryrun:
        info('payload: %s' % json.dumps(payload))
    else:
        publish(payload)


def main(argv):
    parser = ArgumentParser(prog=argv[0])
    parser.add_argument(
        '-c', '--changelog', required=False, default='CHANGES.md', help='Change log file.'
    )
    parser.add_argument('-v', '--version', required=True, help='Version number of the release.')
    parser.add_argument('-r', '--release', required=True, help='Name of the release.')
    parser.add_argument(
        '-d',
        '--dryrun',
        required=False,
        action='store_true',
        help='Display all release info without actually publishing the release.',
    )
    parser.add_argument('--verbose')

    args = parser.parse_args()

    if args.verbose:
        level = DEBUG
    else:
        level = INFO

    basicConfig(
        format='[%(asctime)s][%(levelname)s] %(message)s', datefmt='%Y/%m/%d %H:%M:%S', level=level
    )

    app(args)


if __name__ == '__main__':
    main(argv)
