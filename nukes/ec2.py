
import boto3

from nukes import BaseNuker

ec2_client = boto3.client('ec2')


def get_instance_name(instance):
    ''' Return instance tag:Name, if exists, else InstanceId '''
    if ('Tags' in instance) and (instance['Tags'] != []):
        name = [i['Value'] for i in instance['Tags'] if i['Key'] == 'Name']
        return name[0] if name else instance['InstanceId']

    return instance['InstanceId']


class Instances(BaseNuker):
    def __init__(self):
        super(Instances, self).__init__()
        self.name = 'Instances'
#        self.dependencies = ['s3']

    def list_resources(self):
        _reservations = ec2_client.describe_instances()['Reservations']
        return [get_instance_name(i) for instances in _reservations for i in instances['Instances']]
                


class AMIs(BaseNuker):
    enabled = False
    def __init__(self):
        super(AMIs, self).__init__()
        self.name = 'AMIs'
        self.dependencies = ['Instances']



