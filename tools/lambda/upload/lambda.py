from upload_photo import create_signed_url
from pprint import pprint


def handler(event, context):
    bucket = event['bucket']
    filename = event['filename']
    url = create_signed_url(bucket, filename)
    print(url)
