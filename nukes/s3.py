
import boto3

from nukes import BaseNuker

s3_client = boto3.client('s3')

class S3(BaseNuker):
    def __init__(self):
        super(S3, self).__init__()
        self.name = 's3'
#        self.dependencies = ['ec2']

    def list_resources(self):
        return [i["Name"] for i in s3_client.list_buckets()['Buckets']]

