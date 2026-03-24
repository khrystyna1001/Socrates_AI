import os
import boto3
from botocore.config import Config

def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=os.getenv('S3_ENDPOINT_URL'),
        aws_access_key_id=os.getenv('MINIO_ROOT_USER'),
        aws_secret_access_key=os.getenv('MINIO_ROOT_PASSWORD'),
        config=Config(
            signature_version='s3v4',
            s3={'addressing_style': 'path'}
        )
    )