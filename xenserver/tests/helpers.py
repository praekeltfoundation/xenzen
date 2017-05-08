"""
Test helpers.
"""

from xenserver.models import Template, Zone, AddressPool, XenServer
from xenserver.tests.fake_xen_server import FakeXenServer


HOST_MEM = 64*1024
HOST_CPUS = 16


class FakeXenHost(object):
    """
    A wrapper around a single xen server and its associated API data.
    """
    def __init__(self, hostname, xapi_version=None, mem=HOST_MEM,
                 cpus=HOST_CPUS):
        xapi_version = (1, 2) if xapi_version is None else xapi_version
        self.hostname = hostname
        self.api = FakeXenServer()
        self.host_ref = self.api.add_host(
            xapi_version,
            mem=mem*1024*1024,
            cpu_info={'cpu_count': cpus},
        )
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

    def get_info(self):
        return self.api.hosts[self.host_ref]

    def get_session(self):
        return self.api.getSession()


def new_fake_host(hostname, xapi_version=None, isos=('installer.iso',)):
    """
    Create a new fake host with default setup.
    """
    host = FakeXenHost(hostname, xapi_version)
    host.add_network('eth0', 'xenbr0', gateway='192.168.199.1')
    host.add_network('eth1', 'xenbr1')
    host.add_sr('local', 'Local storage', 'lvm')
    host.add_sr('iso', 'ISOs', 'iso', isos)
    return host


class XenServerHelper(object):
    def __init__(self):
        self.hosts = {}
        self.isos = ["installer.iso"]

    def new_host(self, hostname, xapi_version=None):
        """
        Create a new host with default setup, including default db objects.
        """
        host = new_fake_host(hostname, xapi_version, self.isos)
        self.add_existing_host(host)
        zone = self.db_zone("zone1")
        self.db_addresspool("192.168.199.0/24", "192.168.199.1", zone)
        xs = self.db_xenserver(hostname, zone)
        return (host, xs)

    def add_existing_host(self, host):
        """
        Add an existing host helper to this collection. Primarily useful for
        nonstandard hosts.
        """
        self.hosts[host.hostname] = host

    def db_zone(self, name):
        return Zone.objects.get_or_create(name=name)[0]

    def db_addresspool(self, subnet, gateway, zone, version=4):
        return AddressPool.objects.get_or_create(
            subnet=subnet, gateway=gateway, zone=zone, version=version)[0]

    def get_db_xenserver(self, hostname):
        return XenServer.objects.get(hostname=hostname)

    def get_db_xenserver_dict(self, hostname):
        [xsdict] = XenServer.objects.filter(hostname=hostname).values()
        return xsdict

    def db_xenserver(self, hostname, zone, memory=HOST_MEM, mem_free=HOST_MEM,
                     cores=HOST_CPUS, username="u", password="p"):
        return XenServer.objects.get_or_create(
            hostname=hostname, zone=zone, memory=memory, mem_free=mem_free,
            cores=cores, username=username, password=password)[0]

    def db_template(self, name, cores=1, memory=2048, diskspace=10240,
                    iso="installer.iso"):
        return Template.objects.get_or_create(
            name=name, cores=cores, memory=memory, diskspace=diskspace,
            iso=iso)[0]

    def get_session(self, hostname, username=None, password=None):
        return self.hosts[hostname].get_session()
