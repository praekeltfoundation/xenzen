"""
Some quick and dirty tests for a very small subset of the code.
"""

from django.test import TestCase

from xenserver.models import Template, XenVM
from xenserver.tasks import _create_vm
from xenserver.tests.fake_xen_server import FakeXenServer


class TestCreateVM(TestCase):
    def setup_storage(self, xenserver, iso_names):
        xenserver.add_SR('Local storage', 'lvm')
        isos = xenserver.add_SR('ISOs', 'iso')
        for iso_name in iso_names:
            xenserver.add_VDI(isos, iso_name)

    def test_create_vm_simple(self):
        """
        We can create a new VM using mostly default values.

        TODO: Check that we're actually creating a VM on the backend.
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
        _create_vm(session, vm, template, None, None, None, None, None, None)
        vm.refresh_from_db()
        assert vm.xsref != ''
