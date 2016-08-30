"""
Some quick and dirty tests for a very small subset of the code.
"""

import pytest

from xenserver.models import Template, XenVM
from xenserver.tasks import _create_vm
from xenserver.tests.fake_xen_server import FakeXenServer
from xenserver.tests.matchers import (
    ExpectedXenServerVM, ExpectedXenServerVIF, ExtractValues, MatchSorted)


@pytest.mark.django_db
class TestCreateVM(object):
    def setup_xs_storage(self, xenserver, iso_names=("installer.iso",)):
        self.local_SR = xenserver.add_SR('Local storage', 'lvm')
        self.iso_SR = xenserver.add_SR('ISOs', 'iso')
        for iso_name in iso_names:
            xenserver.add_VDI(self.iso_SR, iso_name)

    def setup_xs_networks(self, xenserver):
        self.pub_net = xenserver.add_network(bridge="xenbr0")
        self.prv_net = xenserver.add_network(bridge="xenbr1")
        self.pub_PIF = xenserver.add_PIF(
            self.pub_net, device="eth0", gateway="10.1.2.3")
        self.prv_PIF = xenserver.add_PIF(self.prv_net, device="eth1")

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
        """
        xenserver = FakeXenServer()
        self.setup_xs_storage(xenserver)
        self.setup_xs_networks(xenserver)
        session = xenserver.getSession()
        template = self.setup_template("footempl")
        vm = self.setup_vm("foovm", template)

        assert vm.xsref == ''
        assert xenserver.VMs == {}

        _create_vm(
            session, vm, template, None, None, None, None, None, None,
            extra_network_bridges=[])

        vm.refresh_from_db()
        assert vm.xsref != ''

        # Make sure the right VIFs and VBDs were created and extract their
        # reference values.
        ev = ExtractValues("VIF", "iso_VBD", "local_VBD")
        self.extract_VIFs(xenserver, vm.xsref, [(self.pub_net, ev.VIF)])
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
            device="0", VM=vm.xsref, network=self.pub_net,
        ) == xenserver.VIFs[ev.VIF.value]

        # The VM should be started.
        assert xenserver.VM_operations == [(vm.xsref, "start")]

    def test_create_vm_second_vif(self):
        """
        We can create a new VM with a second VIF.

        # TODO: Actually implement second network interface support.
        """
        xenserver = FakeXenServer()
        self.setup_xs_storage(xenserver)
        self.setup_xs_networks(xenserver)
        session = xenserver.getSession()
        template = self.setup_template("footempl")
        vm = self.setup_vm("foovm", template)

        assert vm.xsref == ''
        assert xenserver.VMs == {}

        # TODO: Add second network interface.
        _create_vm(
            session, vm, template, None, None, None, None, None, None,
            extra_network_bridges=['xenbr1'])

        vm.refresh_from_db()
        assert vm.xsref != ''

        # Make sure the right VIFs and VBDs were created and extract their
        # reference values.
        ev = ExtractValues("pub_VIF", "prv_VIF", "iso_VBD", "local_VBD")
        self.extract_VIFs(xenserver, vm.xsref, [
            (self.pub_net, ev.pub_VIF),
            (self.prv_net, ev.prv_VIF),
        ])
        self.extract_VBDs(xenserver, vm.xsref, [
            (self.iso_SR, ev.iso_VBD),
            (self.local_SR, ev.local_VBD),
        ])

        # The VM data structure should match the values we passed to
        # _create_vm().
        assert xenserver.VMs.keys() == [vm.xsref]
        assert self.expected_vm(
            template, VIFs=[ev.pub_VIF, ev.prv_VIF],
            VBDs=[ev.iso_VBD, ev.local_VBD],
        ) == xenserver.VMs[vm.xsref]

        # The VIF data structures should match the values we passed to
        # _create_vm().
        assert MatchSorted([ev.pub_VIF, ev.prv_VIF]) == xenserver.VIFs.keys()
        assert ExpectedXenServerVIF(
            device="0", VM=vm.xsref, network=self.pub_net,
        ) == xenserver.VIFs[ev.pub_VIF.value]
        assert ExpectedXenServerVIF(
            device="1", VM=vm.xsref, network=self.prv_net,
        ) == xenserver.VIFs[ev.prv_VIF.value]

        # The VM should be started.
        assert xenserver.VM_operations == [(vm.xsref, "start")]
