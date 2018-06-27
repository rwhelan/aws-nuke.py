
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

    def __list_sgs(self):
        return ec2_client.describe_security_groups()['SecurityGroups']

    def list_resources(self):
        if not ids_only:
            return [sg['GroupName'] for sg in self.__list_sgs() if sg['GroupName'] != 'default']


    def nuke_resources(self):
        sgs = self.__list_sgs()
        for sg in sgs:
            if sg['IpPermissions']:
                for ipperm in sg['IpPermissions']:
                    ec2_client.revoke_security_group_ingress(
                        IpPermissions=[ipperm],
                        GroupId=sg['GroupId']
                    )

            if sg['IpPermissionsEgress']:
                for ipperm in sg['IpPermissionsEgress']:
                    ec2_client.revoke_security_group_egress(
                        IpPermissions=[ipperm],
                        GroupId=sg['GroupId']
                    )
        
        for sg in sgs:
            if sg['GroupName'] != 'default':
                ec2_client.delete_security_group(
                    GroupId=sg['GroupId']
                )



class AMIs(BaseNuker):
    #enabled = False
    def __init__(self):
        super(AMIs, self).__init__()
        self.name = 'amis'

    def list_resources(self, ids_only = False):
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

        if not ids_only:
            return [img['Name'] for img in _images]

        return [img['ImageId'] for img in _images]

    def nuke_resources(self):
        for image in self.list_resources(ids_only=True):
            ec2_client.deregister_image(
                ImageId=image
            )





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

    def nuke_resources(self):
        for snapshot in self.list_resources():
            ec2_client.delete_snapshot(
                SnapshotId=snapshot
            )

    
class EIPs(BaseNuker):
    def __init__(self):
        super(EIPs, self).__init__()
        self.name = 'eips'
        self.dependencies = ['instances']

    def list_resources(self, ids_only = False):
        _addresses = ec2_client.describe_addresses()['Addresses']
        if not ids_only:
            return [addr['PublicIp'] for addr in _addresses]

        return [addr['AllocationId'] for addr in _addresses]

    def nuke_resources(self):
        for addr in self.list_resources(ids_only=True):
            ec2_client.release_address(
                AllocationId=addr
            )



class VpnGateways(BaseNuker):
    def __init__(self):
        super(VpnGateways, self).__init__()
        self.name = 'vpngateways'

    def __list_vgws(self):
        return ec2_client.describe_vpn_gateways()['VpnGateways']

    def list_resources(self):
        return [vgw['VpnGatewayId'] for vgw in self.__list_vgws()]

    def nuke_resources(self):
        vgws = self.__list_vgws()
        for vgw in vgws:
            if vgw['State'] in ('deleted', 'deleting'): continue

            if 'VpcAttachments' in vgw:
                for attachment in vgw['VpcAttachments']:
                    ec2_client.detach_vpn_gateway(
                        VpcId=attachment['VpcId'],
                        VpnGatewayId=vgw['VpnGatewayId']
                    )

            ec2_client.delete_vpn_gateway(
                VpnGatewayId=vgw
            )


class CustomerGateways(BaseNuker):
    def __init__(self):
        super(CustomerGateways, self).__init__()
        self.name = 'customergateways'
        self.dependencies = ['vpngateways']

    def list_resources(self):
        _cgws = ec2_client.describe_customer_gateways()['CustomerGateways']
        return [cgw['CustomerGatewayId'] for cgw in _cgws]

    def nuke_resources(self):
        for cgw in self.list_resources():
            ec2_client.delete_customer_gateway(
                CustomerGatewayId=cgw
            )

'''
class DHCPOptions(BaseNuker):
    def __init__(self):
        super(DHCPOptions, self).__init__()
        self.name = 'dhcpoptions'

    def list_resources(self):
        _dhcpoptions = ec2_client.describe_dhcp_options()['DhcpOptions']
        return [ops['DhcpOptionsId'] for ops in _dhcpoptions]

    def nuke_resources(self):
        for dhcpops in self.list_resources():
            ec2_client.delete_dhcp_options(
                DhcpOptionsId=dhcpops
            )
'''

class KeyPairs(BaseNuker):
    def __init__(self):
        super(KeyPairs, self).__init__()
        self.name = 'keypairs'

    def list_resources(self):
        _keypairs = ec2_client.describe_key_pairs()['KeyPairs']
        return [keypair['KeyName'] for keypair in _keypairs]

    def nuke_resources(self):
        for keypair in self.list_resources():
            ec2_client.delete_key_pair(
                KeyName=keypair
            )


class NatGateways(BaseNuker):
    def __init__(self):
        super(NatGateways, self).__init__()
        self.name = 'natgateways'

    def list_resources(self):
        _ngws = ec2_client.describe_nat_gateways()['NatGateways']
        return [ngw['NatGatewayId'] for ngw in _ngws]

    def nuke_resources(self):
        for ngw in self.list_resources():
            ec2_client.delete_nat_gateway(
                NatGatewayId=ngw
            )


class RouteTables(BaseNuker):
    def __init__(self):
        super(RouteTables, self).__init__()
        self.dependencies = [
            'subnets'
        ]
        self.name = 'routetables'

    def list_resources(self):
        rts_ids = []
        _rtbls = ec2_client.describe_route_tables()['RouteTables']
        for rt in _rtbls:
            if not rt['Associations']:
                rts_ids.append(rt['RouteTableId'])
                continue

            for association in rt['Associations']:
                if ('Main' not in association) or (association['Main'] != True):
                    rts_ids.append(rt['RouteTableId'])

        return rts_ids

    def nuke_resources(self):
        for rt in self.list_resources():
            print(f"deleteing {rt}")
            ec2_client.delete_route_table(
                RouteTableId=rt
            )


class Subnets(BaseNuker):
    def __init__(self):
        super(Subnets, self).__init__()
        self.dependencies = [
            'instances',
            'natgateways',
            'vpcendpointsconnections'
        ]
        self.name = 'subnets'

    def list_resources(self):
        _subnets = ec2_client.describe_subnets()['Subnets']
        return [sbn['SubnetId'] for sbn in _subnets]

    def nuke_resources(self):
        for subnet in self.list_resources():
            ec2_client.delete_subnet(
                SubnetId=subnet
            )


class Volumes(BaseNuker):
    def __init__(self):
        super(Volumes, self).__init__()
        self.dependencies = ['instances']
        self.name = 'volumes'

    def list_resources(self):
        _vols = ec2_client.describe_volumes()['Volumes']
        return [vol['VolumeId'] for vol in _vols]

    def nuke_resources(self):
        [ec2_client.delete_volume(VolumeId=i) for i in self.list_resources()]


class VpcEndpointsConnections(BaseNuker):
    def __init__(self):
        super(VpcEndpointsConnections, self).__init__()
        self.name = 'vpcendpointconnections'

    def list_resources(self):
        _vepc = ec2_client.describe_vpc_endpoint_connections()['VpcEndpointConnections']
        return [vp['VpcEndpointId'] for vp in _vepc]

    def nuke_resources(self):
        [ec2_client.delete_vpc_peering_connection(VpcEndpointId=i) for i in self.list_resources()]


class VpcEndpoints(BaseNuker):
    def __init__(self):
        super(VpcEndpoints, self).__init__()
        self.name = 'vpcendpoints'

    def list_resources(self):
        _vep = ec2_client.describe_vpc_endpoints()['VpcEndpoints']
        return [vp['VpcEndpointId'] for vp in _vep]

    def nuke_resources(self):
        endpoints = self.list_resources()
        if endpoints:
            ec2_client.delete_vpc_endpoints(
                VpcEndpointIds=endpoints
            )


class InternetGateways(BaseNuker):
    def __init__(self):
        super(InternetGateways, self).__init__()
        self.name = 'internetgateways'

    def __list_igws(self):
        return ec2_client.describe_internet_gateways()['InternetGateways']

    def list_resources(self):
        return [igw['InternetGatewayId'] for igw in self.__list_igws()]

    def nuke_resources(self):
        igws = self.__list_igws()
        for igw in igws:
            if ('Attachments' in igw):
                for attachment in igw['Attachments']:
                    ec2_client.detach_internet_gateway(
                        InternetGatewayId=igw['InternetGatewayId'],
                        VpcId=attachment['VpcId']
                    )

            ec2_client.delete_internet_gateway(
                InternetGatewayId=igw['InternetGatewayId']
            )



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
            'customergateways',
            'securitygroups',
            'internetgateways',
            'vpngateways'
        ]
        self.name = 'vpcs'

    def list_resources(self):
        _vpcs = ec2_client.describe_vpcs()['Vpcs']
        return [vpc['VpcId'] for vpc in _vpcs]

    def nuke_resources(self):
        [ec2_client.delete_vpc(VpcId=i) for i in self.list_resources()]
