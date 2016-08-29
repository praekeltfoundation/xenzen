"""
Some quick and dirty tests for a very small subset of the code.
"""

from django.test import TestCase

from xenserver.models import Template, XenVM
from xenserver.tasks import _create_vm
from xenserver.tests.fake_xen_server import FakeXenServer
from xenserver.tests.matchers import (
    ExpectedXenServerVM, ExpectedXenServerVIF, ExtractValues, MatchSorted)


class TestCreateVM(TestCase):
    def setup_xs_storage(self, xenserver, iso_names=("installer.iso",)):
        self.local_SR = xenserver.add_SR('Local storage', 'lvm')
        self.iso_SR = xenserver.add_SR('ISOs', 'iso')
        for iso_name in iso_names:
            xenserver.add_VDI(self.iso_SR, iso_name)

    def setup_template(self, name, cores=1, memory=2048, diskspace=10240,
                       iso="installer.iso"):
        return Template.objects.create(
            name=name, cores=cores, memory=memory, diskspace=diskspace,
            iso=iso)

    def setup_vm(self, name, template, status="Provisioning", **kw):
        params = {
            "sockets": template.cores,
            "memory": template.memory,
        }
        params.update(kw)
        return XenVM.objects.create(
            name="foovm", status="Provisioning", template=template, **params)

    def extract_VIFs(self, xenserver, VM_ref, spec):
        """
        Get the VIFs for the given VM and match them to a list of (network,
        VIF) ref pairs.
        """
        assert MatchSorted(spec) == xenserver.list_network_VIFs_for_VM(VM_ref)

    def extract_VBDs(self, xenserver, VM_ref, spec):
        """
        Get the VBDs for the given VM and match them to a list of (SR, VBD)
        ref pairs.
        """
        assert MatchSorted(spec) == xenserver.list_SR_VBDs_for_VM(VM_ref)

    def expected_vm(self, template, VIFs, VBDs, **kw):
        """
        Build an ExpectedXenServerVM object with some default parameters.
        """
        params = {
            "PV_args": " -- quiet console=hvc0",
            "name_label": "None.None",
            "VCPUs_max": "1",
            "VCPUs_at_startup": "1",
            "memory_static_max": str(template.memory*1024*1024),
            "memory_dynamic_max": str(template.memory*1024*1024),
            "suspend_SR": self.local_SR,
        }
        return ExpectedXenServerVM(
            VIFs=MatchSorted(VIFs), VBDs=MatchSorted(VBDs), **params)

    def test_create_vm_simple(self):
        """
        We can create a new VM using mostly default values.

        TODO: Look at VIFs etc. as well.

        FIXME: This is much hackier than I'd like, but it's a starting point.
        """
        xenserver = FakeXenServer()
        self.setup_xs_storage(xenserver)
        net, _PIF = xenserver.add_net_PIF(gateway='10.1.2.3')
        session = xenserver.getSession()
        template = self.setup_template("footempl")
        vm = self.setup_vm("foovm", template)

        assert vm.xsref == ''
        assert xenserver.VMs == {}

        _create_vm(session, vm, template, None, None, None, None, None, None)

        vm.refresh_from_db()
        assert vm.xsref != ''

        # Make sure the right VIFs and VBDs were created and extract their
        # reference values.
        ev = ExtractValues("VIF", "iso_VBD", "local_VBD")
        self.extract_VIFs(xenserver, vm.xsref, [(net, ev.VIF)])
        self.extract_VBDs(xenserver, vm.xsref, [
            (self.iso_SR, ev.iso_VBD),
            (self.local_SR, ev.local_VBD),
        ])

        # The VM data structure should match the values we passed to
        # _create_vm().
        assert xenserver.VMs.keys() == [vm.xsref]
        assert self.expected_vm(
            template, VIFs=[ev.VIF], VBDs=[ev.iso_VBD, ev.local_VBD],
        ) == xenserver.VMs[vm.xsref]

        # The VIF data structures should match the values we passed to
        # _create_vm().
        assert xenserver.VIFs.keys() == [ev.VIF.value]
        assert ExpectedXenServerVIF(
            VM=vm.xsref, network=net,
        ) == xenserver.VIFs[ev.VIF.value]

        # The VM should be started.
        assert xenserver.VM_operations == [(vm.xsref, "start")]
