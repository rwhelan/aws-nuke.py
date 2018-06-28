
import time

import boto3

from nukes import BaseNuker

efs_client = boto3.client('efs')


class EFS(BaseNuker):
    def __init__(self):
        super(EFS, self).__init__()
        self.name = 'efs'

    def list_resources(self, ids_only = False):
        _filesystems = efs_client.describe_file_systems()['FileSystems']
        if not ids_only:
            efs_list = []
            for efs in _filesystems:

                if 'Name' in efs and efs['Name'] != '':
                    efs_list.append(efs['Name'])
                else:
                    efs_list.append(efs['FileSystemId'])

            return efs_list

        return [i['FileSystemId'] for i in _filesystems]

    def nuke_resources(self):
        efs_ids = self.list_resources(ids_only=True)
        for efs in efs_ids:
            for mount_target in efs_client.describe_mount_targets(FileSystemId=efs)['MountTargets']:
                efs_client.delete_mount_target(
                    MountTargetId=mount_target['MountTargetId']
                )

            while True:
                mount_targets = efs_client.describe_mount_targets(FileSystemId=efs)
                print(mount_targets['MountTargets'])
                if len(mount_targets['MountTargets']):
                    time.sleep(10.0)
                    print(mount_targets['MountTargets'])
                else:
                    break

            efs_client.delete_file_system(
                FileSystemId=efs
            )

