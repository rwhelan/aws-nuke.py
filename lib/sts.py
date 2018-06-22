

from boto3 import client

sts_client = client('sts')
caller_identity = sts_client.get_caller_identity()
account_number = caller_identity['Account']
