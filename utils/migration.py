# Main classes

import time
import threading

from copy import copy
from enum import Enum
from random import random


class CloudType(Enum):
    """ Supported cloud services """
    aws = 1
    azure = 2
    vsphere = 3
    vcloud = 4


class MigrationState(Enum):
    """ Migration process states """
    not_started = 1
    running = 2
    error = 3
    success = 4


class Credentials:
    """ Credentials for workload connection"""

    def __init__(self, username="", password="", domain=""):
        self.username = username
        self.password = password
        self.domain = domain


class MountPoint:
    """ Mount point """

    def __init__(self, name: str):
        self.__name = name
        self.__total_size = int(random() * 1e6)

    def __eq__(self, other):
        return __name == other.name

    @property
    def name(self) -> str:
        return self.__name

    @property
    def total_size(self) -> int:
        return self.__total_size


class Workload:
    """ Workload """

    def __init__(self, ip: str):
        self.__ip = ip
        self.__credentials = Credentials()
        self.storages = []

    def set_credentials(self, username: str, password: str, domain=""):
        self.__credentials.username = username
        self.__credentials.password = password
        self.__credentials.domain = domain

    def connect(self) -> bool:
        if not self.__ip:
            raise Exception("IP address can't be empty")
        elif not self.__credentials.username:
            raise Exception("Username can't be empty")
        elif not self.__credentials.password:
            raise Exception("Password can't be empty")

        return True

    def authorize(self):
        return self.__credentials.username == "admin" and self.__credentials.password == "admin"


class MigrationTarget:
    """ Migration target """

    def __init__(self, cloud_type: CloudType):
        if not cloud_type in CloudType.__members__:
            raise Exception("Selected cloud type is not supported")

        self.cloud_type = cloud_type
        self.target_vm = None
        self.__cloud_credentials = Credentials()

    def set_cloud_credentials(self, username: str, password: str, domain=""):
        self.__cloud_credentials.username = username
        self.__cloud_credentials.password = password
        self.__cloud_credentials.domain = domain

    def connect_to_cloud(self) -> bool:
        return True

    def connect_to_target_vm(self) -> bool:
        if not self.target_vm:
            return False
        return self.target_vm.connect() and self.target_vm.authorize()


class Migration:
    """ Migration process from source VM to target VM in cloud service """

    def __init__(self, mount_points: list, source: Workload, target: MigrationTarget):
        self.mount_points = mount_points
        self.source = source
        self.target = target
        self.__state = MigrationState.not_started

    def check_parameters(self) -> bool:
        if len(self.mount_points) == 0:
            return False
        return true

    @property
    def state(self) -> str:
        """ Get state of migration process """
        return str(self.__state)

    def __run_worker(self):
        time.sleep(15)

        # Not allow running migration when volume C:\ is not allowed
        has_volume_c = False
        for item in self.__mount_points:
            if item.name.upper() == "C:\\":
                has_volume_c = True
                break
        if not has_volume_c:
            self.__state = MigrationState.error
            return

        # Create connection and authorize in source VM
        connection_result = self.__source.connect() and self.__source.authorize()

        # Authorize in cloud service and connect to target VM
        connection_result = connection_result and self.__target.connect_to_cloud(
        ) and self.__target.connect_to_target_vm()

        if not connection_result:
            self.__state = MigrationState.error
            return

        # Copy allowed mount point from source to target
        for item in self.__mount_points:
            for source_mount in self.__source.storages:
                if item.name.upper() == source_mount.name.upper():
                    mount_copy = copy(source_mount)
                    self.__target.target_vm.storages.append(mount_copy)
                    break

        self.__state = MigrationState.success

    def run(self):
        """ Start migration process """
        self.__state = MigrationState.running

        t = threading.Thread(target=self.__run_worker)
        t.start()

    def stop(self):
        """ Stop migration process """
        self.__state = MigrationState.not_started
