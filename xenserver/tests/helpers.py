"""
Test helpers.
"""

from xenserver.tests.fake_xen_server import FakeXenServer


class FakeXenHost(object):
    """
    A wrapper around a single xen server and its associated API data.
    """
    def __init__(self, hostname, xenapi_version=None):
        xenapi_version = (1, 2) if xenapi_version is None else xenapi_version
        self.hostname = hostname
        self.api = FakeXenServer()
        self.host_ref = self.api.add_host(xenapi_version[0], xenapi_version[1])
        self.api.add_pool(self.host_ref)
        self.net = {}
        self.pif = {}
        self.sr = {}

    def add_network(self, device, bridge, gateway=''):
        """
        Add a network and its associated PIF.
        """
        net = self.api.add_network(bridge=bridge)
        self.net[device] = net
        self.pif[device] = self.api.add_PIF(net, device, gateway=gateway)

    def add_sr(self, name, label, kind, vdis=()):
        """
        Add an SR and optionally some VDIs.
        """
        self.sr[name] = self.api.add_SR(label, kind)
        for vdi in vdis:
            self.api.add_VDI(self.sr[name], vdi)

    def get_session(self):
        return self.api.getSession()


def new_host_helper(hostname, xenapi_version=None, isos=('installer.iso',)):
    host = FakeXenHost(hostname, xenapi_version)
    host.add_network('eth0', 'xenbr0', gateway='192.168.199.1')
    host.add_network('eth1', 'xenbr1')
    host.add_sr('local', 'Local storage', 'lvm')
    host.add_sr('iso', 'ISOs', 'iso', isos)
    return host


class XenServerCollection(object):
    def __init__(self):
        self.hosts = {}
        self.isos = ["installer.iso"]

    def new_host(self, hostname, xenapi_version=None):
        self.add_existing_host(
            new_host_helper(hostname, xenapi_version, self.isos))

    def add_existing_host(self, host):
        """
        This is for adding a nonstandard host.
        """
        self.hosts[host.hostname] = host

    def get_session(self, hostname):
        return self.hosts[hostname].get_session()
