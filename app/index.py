import boto3
from jinja2 import Environment, FileSystemLoader

import settings
from app_logger import logger


def index_generation():
    file_loader = FileSystemLoader('templates')
    env = Environment(loader=file_loader)

    index_template = env.get_template('index.html.j2')

    output = index_template.render(site_locations=settings.site_locations, bucketname=settings.s3_bucket_name)
    index_filename = 'index.html'
    local_path = f'./{index_filename}'
    with open(local_path, 'w') as f:
        f.write(output)
    s3 = boto3.resource('s3')
    bucket_name = settings.s3_bucket_name
    with open(local_path, 'rb') as f:
        bucket = s3.Bucket(bucket_name)
        bucket.put_object(Body=f,
                          Key=index_filename,
                          ContentType='text/html',
                          ACL='public-read')
    logger.info(f'Image saved successfully in S3 bucket: s3://{bucket_name}/{index_filename}')
