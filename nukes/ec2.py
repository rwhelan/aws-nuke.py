
import boto3

from lib import sts
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

    def list_resources(self):
        _reservations = ec2_client.describe_instances()['Reservations']
        return [get_instance_name(i) for instances in _reservations for i in instances['Instances']]


class SecurityGroups(BaseNuker):
    def __init__(self):
        super(SecurityGroups, self).__init__()
        self.name = 'SecurityGroups'
        self.dependencies = ['Instances']

    def list_resources(self):
        _security_groups = ec2_client.describe_security_groups()['SecurityGroups']
        return [sg['GroupName'] for sg in _security_groups if sg['GroupName'] != 'default']


class AMIs(BaseNuker):
    #enabled = False
    def __init__(self):
        super(AMIs, self).__init__()
        self.name = 'amis'

    def list_resources(self):
        _images = ec2_client.describe_images(
            Filters = [
                {
                    "Name": "owner-id",
                    "Values": [
                        sts.account_number
                    ]
                }
            ]
        )['Images']
        return [img['Name'] for img in _images]


class SnapShots(BaseNuker):
    def __init__(self):
        super(SnapShots, self).__init__()
        self.name = 'snapshots'
        self.dependencies = ['amis']

    def list_resources(self):
        _snapshots = ec2_client.describe_snapshots(
            Filters = [
                {
                    "Name": "owner-id",
                    "Values": [
                        sts.account_number
                    ]
                }
            ]
        )['Snapshots']
        return [snap['SnapshotId'] for snap in _snapshots]

    



