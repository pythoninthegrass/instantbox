#!/usr/bin/env python

import docker
import json
import random
import string
import time


class InstantboxManager(object):
    CONTAINER_PREFIX = 'instantbox_managed_'
    TIMEOUT_LABEL = 'org.instantbox.variables.EXPIRATION_TIMESTAMP'
    OS_LIST = None

    def __init__(self):
        self.client = docker.from_env()

        try:
            with open('manifest.json', 'r') as os_manifest:
                self.OS_LIST = json.load(os_manifest)
        except Exception:
            pass

        if self.OS_LIST is None:
            raise Exception(
                'Could not load manifest.json. ' +
                'Download it from https://get.instantbox.org/manifest.json'
            )

        self.AVAILABLE_OS_LIST = []
        for os in self.OS_LIST:
            for ver in os['subList']:
                self.AVAILABLE_OS_LIST.append(ver['osCode'])

    def create_container(self,
                            mem,
                            cpu,
                            os_name,
                            os_timeout,
                            open_port=None):
        if open_port is None:
            port_dict = {}
        else:
            port_dict = {'{}/tcp'.format(open_port): None}

        container_name = self.generate_container_name()
        try:
            container_network = self.client.networks.create(
                name=container_name + '_net',
                driver="bridge",
                internal=True,
            )
            self.client.containers.run(
                image=os_name,
                cpu_period=100000,
                cpu_quota=int('%s0000' % cpu),
                mem_limit='%sm' % mem,
                name=container_name,
                hostname=container_name,
                ports=port_dict,
                restart_policy={'Name': 'always'},
                labels={self.TIMEOUT_LABEL: str.format('{:.0f}', os_timeout)},
                tty=True,
                detach=True,
            )
            container_network.connect(container_name)
            container_network.connect('instantbox_frontend')
        except Exception:
            return None
        else:
            return container_name

    def get_container_ports(self, container_name):
        try:
            ports = self.client.containers.get(
                container_name).attrs['NetworkSettings']['Ports']
            return {
                port: mapped_ports[0]['HostPort']
                if mapped_ports is not None else None
                for port, mapped_ports in ports.items()
            }
        except Exception:
            return None

    def remove_timeout_containers(self):
        for container in self.client.containers.list():
            if container.name.startswith(self.CONTAINER_PREFIX):
                timeout = container.labels.get(self.TIMEOUT_LABEL)
                if timeout is not None and float(timeout) < time.time():
                    self.remove_container(container.name)

    def remove_container(self, container_id) -> bool:
        try:
            container = self.client.containers.get(container_id)
            if container.name.startswith(self.CONTAINER_PREFIX):
                container.remove(force=True)
                container_network = self.client.networks.get(
                    network_id=container.name + '_net',
                )
                container_network.remove()
        except docker.errors.NotFound:
            return True
        else:
            if container.name.startswith(self.CONTAINER_PREFIX):
                container.remove(force=True)
            return True

    def is_os_available(self, os_code=None) -> bool:
        return os_code is not None and os_code in self.AVAILABLE_OS_LIST

    def generate_container_name(self) -> str:
        return self.CONTAINER_PREFIX + ''.join(
            random.sample(string.ascii_lowercase + string.digits, 16))


if __name__ == '__main__':
    test = InstantboxManager()
    container_name = test.create_container('512', 1,
                                           'instantbox/ubuntu:latest',
                                           time.time())
    test.get_container_ports(container_name)
    test.remove_timeout_containers()
    test.remove_container(container_name)
