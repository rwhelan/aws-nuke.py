
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
        self.name = 'instances'

    def list_resources(self, ids_only = False):
        _reservations = ec2_client.describe_instances()['Reservations']
        if not ids_only:
            return [get_instance_name(i) for instances in _reservations for i in instances['Instances']]
        else:
            return [i['InstanceId'] for instances in _reservations for i in instances['Instances']]

    def nuke_resources(self):
        instance_ids = self.list_resources(ids_only=True)
        id_lists = [instance_ids[i:i+10] for i in range(0, len(instance_ids), 10)]
        for id_list in id_lists:
            ec2_client.terminate_instances(InstanceIds=id_list)



class SecurityGroups(BaseNuker):
    def __init__(self):
        super(SecurityGroups, self).__init__()
        self.name = 'securitygroups'
        self.dependencies = ['instances']

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

    
class EIPs(BaseNuker):
    def __init__(self):
        super(EIPs, self).__init__()
        self.name = 'eips'
        self.dependencies = ['instances']

    def list_resources(self):
        _addresses = ec2_client.describe_addresses()['Addresses']
        return [addr['PublicIp'] for addr in _addresses]


class VpnGateways(BaseNuker):
    def __init__(self):
        super(VpnGateways, self).__init__()
        self.name = 'vpngateways'

    def list_resources(self):
        _vgws = ec2_client.describe_vpn_gateways()['VpnGateways']
        return [vgw['VpnGatewayId'] for vgw in _vgws]


class CustomerGateways(BaseNuker):
    def __init__(self):
        super(CustomerGateways, self).__init__()
        self.name = 'customergateways'
        self.dependencies = ['vpngateways']

    def list_resources(self):
        _cgws = ec2_client.describe_customer_gateways()['CustomerGateways']
        return [cgw['CustomerGatewayId'] for cgw in _cgws]


class DHCPOptions(BaseNuker):
    def __init__(self):
        super(DHCPOptions, self).__init__()
        self.name = 'dhcpoptions'

    def list_resources(self):
        _dhcpoptions = ec2_client.describe_dhcp_options()['DhcpOptions']
        return [ops['DhcpOptionsId'] for ops in _dhcpoptions]


class KeyPairs(BaseNuker):
    def __init__(self):
        super(KeyPairs, self).__init__()
        self.name = 'keypairs'

    def list_resources(self):
        _keypairs = ec2_client.describe_key_pairs()['KeyPairs']
        return [keypair['KeyName'] for keypair in _keypairs]


class NatGateways(BaseNuker):
    def __init__(self):
        super(NatGateways, self).__init__()
        self.name = 'natgateways'

    def list_resources(self):
        _ngws = ec2_client.describe_nat_gateways()['NatGateways']
        return [ngw['NatGatewayId'] for ngw in _ngws]


class RouteTables(BaseNuker):
    def __init__(self):
        super(RouteTables, self).__init__()
        self.name = 'routetables'

    def list_resources(self):
        _rtbls = ec2_client.describe_route_tables()['RouteTables']
        return [rt['RouteTableId'] for rt in _rtbls]


class Subnets(BaseNuker):
    def __init__(self):
        super(Subnets, self).__init__()
        self.dependencies = [
            'instances',
            'routetables',
            'natgateways',
            'vpcendpointsconnections'
        ]
        self.name = 'subnets'

    def list_resources(self):
        _subnets = ec2_client.describe_subnets()['Subnets']
        return [sbn['SubnetId'] for sbn in _subnets]


class Volumes(BaseNuker):
    def __init__(self):
        super(Volumes, self).__init__()
        self.dependencies = ['instances']
        self.name = 'volumes'

    def list_resources(self):
        _vols = ec2_client.describe_volumes()['Volumes']
        return [vol['VolumeId'] for vol in _vols]


class VpcEndpointsConnections(BaseNuker):
    def __init__(self):
        super(VpcEndpointsConnections, self).__init__()
        self.name = 'vpcendpointconnections'

    def list_resources(self):
        _vepc = ec2_client.describe_vpc_endpoint_connections()['VpcEndpointConnections']
        return [vp['VpcEndpointId'] for vp in _vepc]


class VpcEndpoints(BaseNuker):
    def __init__(self):
        super(VpcEndpoints, self).__init__()
        self.name = 'vpcendpoints'

    def list_resources(self):
        _vep = ec2_client.describe_vpc_endpoints()['VpcEndpoints']
        return [vp['VpcEndpointId'] for vp in _vep]


class Vpcs(BaseNuker):
    def __init__(self):
        super(Vpcs, self).__init__()
        self.dependencies = [
            'instances',
            'routetables',
            'natgateways',
            'vpcendpointsconnections',
            'vpcendpoints',
            'routetables',
            'dhcpoptions',
            'customergateways',
            'vpngateways',
            'securitygroups'
        ]
        self.name = 'vpcs'

    def list_resources(self):
        _vpcs = ec2_client.describe_vpcs()['Vpcs']
        return [vpc['VpcId'] for vpc in _vpcs]