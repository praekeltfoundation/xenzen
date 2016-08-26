"""
Some quick and dirty tests for a very small subset of the code.
"""

from django.test import TestCase

from xenserver.models import Template, XenVM
from xenserver.tasks import _create_vm
from xenserver.tests.fake_xen_server import FakeXenServer
from xenserver.tests.matchers import (
    ExpectedXenServerVM, ExpectedXenServerVIF, ExtractValue)


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

        # The VM data structure should match the values we passed to
        # _create_vm().
        ev_VIF = ExtractValue("VIF")
        ev_VBD1 = ExtractValue("VBD1")
        ev_VBD2 = ExtractValue("VBD2")
        exvm = ExpectedXenServerVM(
            PV_args=" -- quiet console=hvc0",
            name_label="None.None",
            VCPUs_max="1",
            VCPUs_at_startup="1",
            memory_static_max=str(2048*1024*1024),
            memory_dynamic_max=str(2048*1024*1024),
            suspend_SR=self.local_sr,
            VIFs=[ev_VIF],
            VBDs=[ev_VBD1, ev_VBD2],
        )
        assert xenserver.VMs.keys() == [vm.xsref]
        exvm.assertMatch(xenserver.VMs[vm.xsref])

        # The VIF data structures should match the values we passed to
        # _create_vm().
        exvif = ExpectedXenServerVIF(VM=vm.xsref, network=net)
        assert xenserver.VIFs.keys() == [ev_VIF.value]
        exvif.assertMatch(xenserver.VIFs[ev_VIF.value])

        # The VM should be started.
        assert xenserver.VM_operations == [(vm.xsref, "start")]
