"""
Some quick and dirty tests for a very small subset of the code.
"""

import pytest

from xenserver.models import Template, XenVM
from xenserver import tasks
from xenserver.tests.helpers import new_host_helper
from xenserver.tests.matchers import (
    ExpectedXenServerVM, ExpectedXenServerVIF, ExtractValues, MatchSorted)


@pytest.mark.django_db
class TestCreateVM(object):

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

    def expected_vm(self, template, local_SR, VIFs, VBDs, **kw):
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
            "suspend_SR": local_SR,
        }
        return ExpectedXenServerVM(
            VIFs=MatchSorted(VIFs), VBDs=MatchSorted(VBDs), **params)

    xenapi_versions = pytest.mark.parametrize('xenapi_version',
                                              [(1, 1), (1, 2)])

    @xenapi_versions
    def test_create_vm_simple(self, xenapi_version):
        """
        We can create a new VM using mostly default values.
        """
        xsh = new_host_helper('xenserver01.local', xenapi_version)
        template = self.setup_template("footempl")
        vm = self.setup_vm("foovm", template)

        assert vm.xsref == ''
        assert xsh.api.VMs == {}

        tasks._create_vm(
            xsh.get_session(), vm, template,
            None, None, None, None, None, None, extra_network_bridges=[])

        vm.refresh_from_db()
        assert vm.xsref != ''

        # Make sure the right VIFs and VBDs were created and extract their
        # reference values.
        ev = ExtractValues("VIF", "iso_VBD", "local_VBD")
        self.extract_VIFs(xsh.api, vm.xsref, [(xsh.net['eth0'], ev.VIF)])
        self.extract_VBDs(xsh.api, vm.xsref, [
            (xsh.sr['iso'], ev.iso_VBD),
            (xsh.sr['local'], ev.local_VBD),
        ])

        # The VM data structure should match the values we passed to
        # _create_vm().
        assert xsh.api.VMs.keys() == [vm.xsref]
        assert self.expected_vm(
            template, xsh.sr['local'], VIFs=[ev.VIF],
            VBDs=[ev.iso_VBD, ev.local_VBD],
        ) == xsh.api.VMs[vm.xsref]

        # The VIF data structures should match the values we passed to
        # _create_vm().
        assert xsh.api.VIFs.keys() == [ev.VIF.value]
        assert ExpectedXenServerVIF(
            device="0", VM=vm.xsref, network=xsh.net['eth0'],
        ) == xsh.api.VIFs[ev.VIF.value]

        # The VM should be started.
        assert xsh.api.VM_operations == [(vm.xsref, "start")]

    @xenapi_versions
    def test_create_vm_second_vif(self, xenapi_version):
        """
        We can create a new VM with a second VIF.
        """
        xsh = new_host_helper('xenserver01.local', xenapi_version)
        template = self.setup_template("footempl")
        vm = self.setup_vm("foovm", template)

        assert vm.xsref == ''
        assert xsh.api.VMs == {}

        tasks._create_vm(
            xsh.get_session(), vm, template,
            None, None, None, None, None, None,
            extra_network_bridges=['xenbr1'])

        vm.refresh_from_db()
        assert vm.xsref != ''

        # Make sure the right VIFs and VBDs were created and extract their
        # reference values.
        ev = ExtractValues("pub_VIF", "prv_VIF", "iso_VBD", "local_VBD")
        self.extract_VIFs(xsh.api, vm.xsref, [
            (xsh.net['eth0'], ev.pub_VIF),
            (xsh.net['eth1'], ev.prv_VIF),
        ])
        self.extract_VBDs(xsh.api, vm.xsref, [
            (xsh.sr['iso'], ev.iso_VBD),
            (xsh.sr['local'], ev.local_VBD),
        ])

        # The VM data structure should match the values we passed to
        # _create_vm().
        assert xsh.api.VMs.keys() == [vm.xsref]
        assert self.expected_vm(
            template, xsh.sr['local'], VIFs=[ev.pub_VIF, ev.prv_VIF],
            VBDs=[ev.iso_VBD, ev.local_VBD],
        ) == xsh.api.VMs[vm.xsref]

        # The VIF data structures should match the values we passed to
        # _create_vm().
        assert MatchSorted([ev.pub_VIF, ev.prv_VIF]) == xsh.api.VIFs.keys()
        assert ExpectedXenServerVIF(
            device="0", VM=vm.xsref, network=xsh.net['eth0'],
        ) == xsh.api.VIFs[ev.pub_VIF.value]
        assert ExpectedXenServerVIF(
            device="1", VM=vm.xsref, network=xsh.net['eth1'],
        ) == xsh.api.VIFs[ev.prv_VIF.value]

        # The VM should be started.
        assert xsh.api.VM_operations == [(vm.xsref, "start")]
