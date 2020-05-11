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


DEFAULT_FROM_ADDRESS = 'postmaster@%s' % environ['APPLICATION_DOMAIN_NAME']


def render_template(template, context):
    tmpl = get_template(template)
    return tmpl.render(context)


def download_and_encode_thumbnails(owner_id, media_items):
    for media_item in media_items:
        path = media_item['file_path']
        url = media_item['thumbnail_url']
        with tempfile.NamedTemporaryFile() as tmp:
            with urllib.request.urlopen(url) as response, open(tmp.name, 'wb') as out:
                shutil.copyfileobj(response, out)
            with open(tmp.name, 'rb') as file:
                init_mime_image(file.read(), media_item)


def init_mime_image(bytes, media_item):
    image = MIMEImage(bytes, name=media_item['basename'])
    image.add_header('Content-ID', '<%s>' % media_item['item_id'])
    image.add_header('Content-Location', media_item['media_item_url'])
    media_item['content_id'] = media_item['item_id']
    media_item['encoded'] = image
