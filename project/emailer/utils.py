from logging import debug
import tempfile
import urllib
import shutil
from email.mime.image import MIMEImage
from os import environ
from json import dumps, loads
from boto3 import resource
from tempfile import NamedTemporaryFile
from PIL import Image
from base64 import b64encode

from django.template.loader import get_template
from django.template import Context


def render_template(template, context):
    tmpl = get_template(template)
    return tmpl.render(context)


def download_and_encode_thumbnails(owner_id, media_items, dims='222x222'):
    if environ['ENVIRONMENT'] == 'local':
        for media_item in media_items:
            path = media_item['file_path'].replace('/', '%2f')
            url = f'http://localhost:8182/iiif/2/{path}/square/pct:33/0/default.jpg'
            with tempfile.NamedTemporaryFile() as tmp:
                with urllib.request.urlopen(url) as response, open(tmp.name, 'wb') as out:
                    shutil.copyfileobj(response, out)
                with open(tmp.name, 'rb') as file:
                    init_mime_image(file.read(), media_item)
    else:
        bucket = environ['MEDIA_UPLOAD_BUCKET_NAME']
        for media_item in media_items:
            image_id = media_item['image_id']
            key = f'{owner_id}/{image_id}.{type}'
            with NamedTemporaryFile(suffix=f'.{type}') as tmp:
                info(f'downloading {key} from s3')
                get_image_from_s3(bucket, key, tmp.name)
                with open(tmp.name, 'rb') as file:
                    debug(f'creating thumbnail with dimensions: {dims}')
                    im = Image.open(file.name)
                    im.thumbnail(dims, Image.ANTIALIAS)
                    im.save(file.name)
                with open(tmp.name, 'rb') as file:
                    encoded_items['image_id'] = init_mime_image(file.read(), media_item)
                    debug('encoding thumbnail as a MIMEImage')


def get_image_from_s3(bucket, key, tempfile):
    debug(f'getting image from bucket with key: {bucket}::{key}')
    s3 = resource('s3')
    b = s3.Bucket(bucket)
    b.download_file(key, tempfile)
    debug(f'image downloaded from s3 and stored at: {tempfile}')


def init_mime_image(bytes, media_item):
    image = MIMEImage(bytes, name=media_item['basename'])
    image.add_header('Content-ID', '<%s>' % media_item['image_id'])
    image.add_header('Content-Location', media_item['file_path'])
    media_item['content_id'] = media_item['image_id']
    media_item['encoded'] = image
