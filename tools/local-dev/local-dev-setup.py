#!/usr/bin/env python3

from sys import argv
from argparse import ArgumentParser
from logging import debug, info, INFO, DEBUG, basicConfig
from pathlib import Path
from glob import glob
from shutil import copyfile
from uuid import uuid4
import os
import hashlib
import re
import subprocess

PROCESSOR_DIR = '/Users/ebridges/Documents/elektron-working/elektrum/processor'
PROCESSOR_ENV = {
    'DB_JDBC_URL': 'jdbc:postgresql://127.0.0.1/media_info',
    'DB_USERNAME': 'elektrondba',
    'DB_PASSWORD': 'elektron-dba',
    'IMAGE_ROOT': '',
}


def process_image(bucket_root, des):
    info(f'processing image at location {bucket_root}/{des}')
    PROCESSOR_ENV['IMAGE_ROOT'] = bucket_root
    if not os.path.exists(f'{PROCESSOR_DIR}/build/libs/elektrum-processor-DEV.jar'):
        info(f'processor not compiled, building first.')
        subprocess.run(['./gradlew', 'fatJar'], cwd=PROCESSOR_DIR)
    subprocess.run(
        ['java', '-jar', f'{PROCESSOR_DIR}/build/libs/elektrum-processor-DEV.jar', '-f', des],
        cwd=bucket_root,
        env=PROCESSOR_ENV,
    )


def md5sum(filename):
    hash_md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def manifest_write(mf, src, des):
    chksum = md5sum(src)
    mf.write('%s,%s,%s\n' % (src, des, chksum))


def needs_processing(manifest, filename):
    '''
    `filename` needs processing when either:
    (a): it does not exist in the manifest, or
    (b): it exists in the manifest, but the file's chksum
         differs from the manifest's record of the chksum
    '''
    with open(manifest, 'r') as mf:
        for line in mf:
            if re.search(filename, line):
                (src, des, mfsum) = line.strip().split(',')
                filesum = md5sum(filename)
                debug(f'{filesum} == {mfsum}')
                if filesum != mfsum:
                    info('existing checksum does not match, image needs processing.')
                    return True
                else:
                    info('existing checksum matches, image does not need processing.')
                    return False
        info('image not currently in manifest, so it needs processing.')
        return True


def bucket_dir(bucket, user_id):
    bucket_path = '%s/%s' % (str(Path(bucket).resolve()), user_id)
    if not os.path.exists(bucket_path):
        os.makedirs(bucket_path)
    return bucket_path


def dest_filename(extension='jpg'):
    return '%s.%s' % (uuid4(), extension)


def list_files(root_dir):
    return [str(Path(f).resolve()) for f in glob(f'{root_dir}/*.jpg')]


# bucket-folder: {fully-qualified-path}/{args.test_images_bucket}
# user-bucket-folder: {bucket-folder}/{args.user_id}
# user-bucket-name: {args.test_images_bucket}/{args.user_id}
# image-key: {args.test_images_bucket}/{args.user_id}/{image_id}.{ext}
def app(args):
    debug(f'app() called with args: {args}')

    bucket_folder = bucket_dir(args.test_images_bucket, args.user_id)
    debug(f'bucket: {bucket_folder}')

    bucket_root = Path(bucket_folder).parent
    debug(f'bucket root: {bucket_root}')

    manifest = '%s/.manifestdb' % bucket_folder
    Path(manifest).touch(exist_ok=True)
    debug(f'manifestdb: {manifest}')

    with open(manifest, 'a+') as mf:
        for src in list_files(args.test_images):
            if needs_processing(manifest, src):
                des_file = dest_filename()
                des = '%s/%s' % (bucket_folder, des_file)
                info(f'copying {src} to {des}')
                manifest_write(mf, src, des)
                copyfile(src, des)
                process_image(bucket_root, f'{args.user_id}/{des_file}')


def main(argv):
    parser = ArgumentParser(prog=argv[0])
    parser.add_argument('-u', '--user-id', required=True, help='User ID of dev test user.')
    parser.add_argument('-s', '--test-images', required=True, help='Folder containing test images.')
    parser.add_argument(
        '-b', '--test-images-bucket', required=False, help='Destination folder for test images.'
    )
    parser.add_argument('-v', '--verbose', default=False, action='store_true')

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
