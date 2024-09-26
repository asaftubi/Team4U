# pip install boto3
import os
import boto3
from dotenv import load_dotenv
from botocore.exceptions import NoCredentialsError

# Load the .env file
load_dotenv()


def upload_to_s3(file_name, bucket, object_name=None):
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Create an S3 client with credentials from .env
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )

    try:
        s3.upload_file(file_name, bucket, object_name)
        print(f"File {file_name} uploaded successfully to {bucket}/{object_name}")
    except FileNotFoundError:
        print(f"The file {file_name} was not found.")
    except NoCredentialsError:
        print("Credentials not available.")


# Example usage
file_name = 'C:/Users/user/Desktop/projects/Team4U/team4U/slack_messages.csv'
bucket_name = 'kb-team4u'
object_name = 'testAsaf'

upload_to_s3(file_name, bucket_name, object_name)
