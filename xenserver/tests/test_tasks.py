"""
Some quick and dirty tests for a very small subset of the code.
"""

from django.test import TestCase

from xenserver.models import Template, XenVM
from xenserver.tasks import _create_vm
from xenserver.tests.fake_xen_server import FakeXenServer


class NVType(object):
    """
    An object to represent a missing value.
    """
    def __repr__(self):
        return "<NO VALUE>"


NO_VALUE = NVType()


class AVType(object):
    """
    An object to represent any value.
    """
    def __repr__(self):
        return "<ANY VALUE>"

    def __eq__(self, other):
        return True


ANY_VALUE = AVType()


class ExpectedXenServerVM(object):
    """
    A matcher for a XenServer VM object.
    """
    default_fields = {
        'name_label': NO_VALUE,
        'name_description': '',
        'user_version': '1',
        'affinity': '',
        'is_a_template': False,
        'auto_power_on': False,
        'memory_static_max': NO_VALUE,
        'memory_static_min': '536870912',
        'memory_dynamic_max': NO_VALUE,
        'memory_dynamic_min': '536870912',
        'VCPUs_max': NO_VALUE,
        'VCPUs_at_startup': NO_VALUE,
        'VCPUs_params': {},
        'actions_after_shutdown': 'destroy',
        'actions_after_reboot': 'restart',
        'actions_after_crash': 'restart',
        'PV_kernel': '',
        'PV_ramdisk': '',
        'PV_bootloader': 'eliloader',
        'PV_bootloader_args': '',
        'PV_legacy_args': '',
        'HVM_boot_policy': '',
        'HVM_boot_params': {},
        'platform': {
            'nx': 'true',
            'apic': 'true',
            'viridian': 'true',
            'pae': 'true',
            'acpi': '1',
        },
        'PCI_bus': '',
        'other_config': {
            'auto_poweron': 'true',
            'mac_seed': ANY_VALUE,
            'install-distro': 'debianlike',
            'base_template_name': 'Ubuntu Precise Pangolin 12.04 (64-bit)',
            'install-arch': 'amd64',
            'install-methods': 'cdrom,http,ftp',
            'install-repository': 'cdrom',
            'debian-release': 'precise',
            'linux_template': 'true'
        },
        'recommendations': '',
        'PV_args': NO_VALUE,
        'suspend_SR': NO_VALUE,
    }

    def __init__(self, **fields):
        self.fields = fields
        self.expected_fields = {}
        self.expected_fields.update(self.default_fields)
        self.expected_fields.update(self.fields)
        self.expected_fields['other_config']['mac_seed']

    def assertMatch(self, other):
        assert self.expected_fields == other


class TestCreateVM(TestCase):
    def setup_storage(self, xenserver, iso_names):
        self.local_sr = xenserver.add_SR('Local storage', 'lvm')
        isos = xenserver.add_SR('ISOs', 'iso')
        for iso_name in iso_names:
            xenserver.add_VDI(isos, iso_name)

    def test_create_vm_simple(self):
        """
        We can create a new VM using mostly default values.

        TODO: Look at VIFs etc. as well.

        FIXME: This is much hackier than I'd like, but it's a starting point.
        """
        xenserver = FakeXenServer()
        self.setup_storage(xenserver, ['installer.iso'])
        net = xenserver.add_network()
        xenserver.add_PIF(net, gateway='10.1.2.3')
        session = xenserver.getSession()
        template = Template.objects.create(
            name="footempl", cores=1, memory=2048, diskspace=10240,
            iso='installer.iso')
        vm = XenVM.objects.create(
            name="foovm", status="Provisioning", sockets=template.cores,
            memory=template.memory, template=template)

        assert vm.xsref == ''
        assert xenserver.VMs == {}

        _create_vm(session, vm, template, None, None, None, None, None, None)

        vm.refresh_from_db()
        assert vm.xsref != ''
        exvm = ExpectedXenServerVM(
            PV_args=" -- quiet console=hvc0",
            name_label="None.None",
            VCPUs_max="1",
            VCPUs_at_startup="1",
            memory_static_max=str(2048*1024*1024),
            memory_dynamic_max=str(2048*1024*1024),
            suspend_SR=self.local_sr,
        )
        assert len(xenserver.VMs) == 1
        exvm.assertMatch(xenserver.VMs[vm.xsref])
