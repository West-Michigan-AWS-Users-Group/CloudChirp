import os

import boto3

import settings
from app_logger import logger


def upload_auto_attendants():
    s3 = boto3.resource('s3')
    bucket_name = settings.s3_bucket_name

    for site in settings.site_locations:
        for file_suffix in settings.file_names:
            for file_extension in ['txt', 'wav']:
                file_name = f'{site["site_abbv"]}_{file_suffix}.{file_extension}'
                file_directory = f'{site["site_abbv"]}'
                local_path = f'./{file_directory}/{file_name}'
                with open(local_path, 'rb') as f:
                    bucket = s3.Bucket(bucket_name)
                    bucket.put_object(Body=f,
                                      Key=f'{file_directory}/{file_name}',
                                      ACL='public-read')
                logger.info(f'Image saved successfully in S3 bucket: s3://{bucket_name}/{file_directory}/{file_name}')
                # Clean up local file
                os.remove(local_path)
                logger.info(f'Local file {local_path} removed.')
    for site in settings.site_locations:
        directory = f'./{site["site_abbv"]}'
        if os.path.isdir(directory) and not os.listdir(directory):
            os.rmdir(directory)
        else:
            logger.error(f'The directory "{directory}" is not empty or does not exist.')
        logger.info(f'Directory {directory} removed.')
