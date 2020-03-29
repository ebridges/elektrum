import tempfile
import urllib
import shutil
from email.mime.image import MIMEImage

from django.template.loader import get_template
from django.template import Context

THUMBNAIL_URL = 'http://localhost:8182/iiif/2/%s/square/pct:33/0/default.jpg'


def render_template(template, context):
    tmpl = get_template(template)
    return tmpl.render(context)


def download_and_encode_thumbnails(media_items):
    for media_item in media_items:
        url_encoded = media_item['file_path'].replace('/', '%2f')
        thumbnail_url = THUMBNAIL_URL % url_encoded
        encoded = mime_encode_file_at_url(thumbnail_url, media_item['basename'])
        encoded.add_header('Content-ID', '<%s>' % media_item['item_id'])
        media_item['content_id'] = media_item['item_id']
        media_item['encoded'] = encoded


def mime_encode_file_at_url(img_url, filename):
    b64 = None
    mi = None
    with tempfile.NamedTemporaryFile() as tmp:
        with urllib.request.urlopen(img_url) as response, open(tmp.name, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        with open(tmp.name, 'rb') as file:
            return MIMEImage(file.read(), name=filename)
