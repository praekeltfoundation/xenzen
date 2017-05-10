"""
Some quick and dirty tests for a very small subset of the code.
"""

import pytest
from testtools.assertions import assert_that
from testtools.matchers import MatchesSetwise

from xenserver import tasks
from xenserver.tests.helpers import VM_MEM
from xenserver.tests.matchers import (
    ExtractValues, MatchesSetOfLists, MatchesVMNamed, MatchesXenServerVIF,
    MatchesXenServerVM)


def apply_task(task, *args, **kw):
    """
    Wrapper around <task>.apply(...).get() to make sure the task properly
    propagates exceptions, etc.
    """
    task.apply(*args, **kw).get()


@pytest.mark.django_db
class TestCreateVM(object):
    """
    Test xenserver.tasks.create_vm task.
    """

    def extract_VIFs(self, xenserver, VM_ref, spec):
        """
        Get the VIFs for the given VM and match them to a list of (network,
        VIF) ref pairs.
        """
        assert_that(
            xenserver.list_network_VIFs_for_VM(VM_ref),
            MatchesSetOfLists(spec))

    def extract_VBDs(self, xenserver, VM_ref, spec):
        """
        Get the VBDs for the given VM and match them to a list of (SR, VBD)
        ref pairs.
        """
        assert_that(
            xenserver.list_SR_VBDs_for_VM(VM_ref),
            MatchesSetOfLists(spec))

    def matches_vm(self, local_SR, VIFs, VBDs, **kw):
        """
        Build an ExpectedXenServerVM object with some default parameters.
        """
        params = {
            "name_label": "None.None",
            "memory_static_max": str(VM_MEM*1024*1024),
            "memory_dynamic_max": str(VM_MEM*1024*1024),
            "suspend_SR": local_SR,
        }
        return MatchesXenServerVM(
            VIFs=MatchesSetwise(*VIFs), VBDs=MatchesSetwise(*VBDs), **params)

    xapi_versions = pytest.mark.parametrize('xapi_version', [(1, 1), (1, 2)])

    @xapi_versions
    def test_create_vm_simple(self, xapi_version, xs_helper):
        """
        We can create a new VM using mostly default values.
        """
        xsh, xs = xs_helper.new_host('xenserver01.local', xapi_version)
        templ = xs_helper.db_template("default")
        vm = xs_helper.db_xenvm(xs, "foovm", templ, status="Provisioning")

        assert vm.xsref == ''
        assert xsh.api.VMs == {}

        apply_task(tasks.create_vm,
                   [vm, xs, templ, None, None, None, None, None, None],
                   {'extra_network_bridges': []})

        vm.refresh_from_db()
        assert vm.xsref != ''

        # Make sure the right VIFs and VBDs were created and extract their
        # reference values.
        ev = ExtractValues("VIF", "iso_VBD", "local_VBD")
        self.extract_VIFs(xsh.api, vm.xsref, [
            (xsh.net['eth0'], ev.VIF),
        ])
        self.extract_VBDs(xsh.api, vm.xsref, [
            (xsh.sr['iso'], ev.iso_VBD),
            (xsh.sr['local'], ev.local_VBD),
        ])

        # The VM data structure should match the values we passed to
        # create_vm().
        assert xsh.api.VMs.keys() == [vm.xsref]
        assert_that(xsh.api.VMs[vm.xsref], self.matches_vm(
            xsh.sr['local'], VIFs=[ev.VIF], VBDs=[ev.iso_VBD, ev.local_VBD]))

        # The VIF data structures should match the values we passed to
        # create_vm().
        assert xsh.api.VIFs.keys() == [ev.VIF.value]
        assert_that(xsh.api.VIFs[ev.VIF.value], MatchesXenServerVIF(
            device="0", VM=vm.xsref, network=xsh.net['eth0']))

        # The VM should be started.
        assert xsh.api.VM_operations == [(vm.xsref, "start")]

    @xapi_versions
    def test_create_vm_second_vif(self, xapi_version, xs_helper):
        """
        We can create a new VM with a second VIF.
        """
        xsh, xs = xs_helper.new_host('xenserver01.local', xapi_version)
        templ = xs_helper.db_template("default")
        vm = xs_helper.db_xenvm(xs, "foovm", templ, status="Provisioning")

        assert vm.xsref == ''
        assert xsh.api.VMs == {}

        apply_task(tasks.create_vm,
                   [vm, xs, templ, None, None, None, None, None, None],
                   {'extra_network_bridges': ['xenbr1']})

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
        # create_vm().
        assert xsh.api.VMs.keys() == [vm.xsref]
        assert_that(xsh.api.VMs[vm.xsref], self.matches_vm(
            xsh.sr['local'], VIFs=[ev.pub_VIF, ev.prv_VIF],
            VBDs=[ev.iso_VBD, ev.local_VBD]))

        # The VIF data structures should match the values we passed to
        # create_vm().
        assert_that(
            xsh.api.VIFs.keys(), MatchesSetwise(ev.pub_VIF, ev.prv_VIF))
        assert_that(xsh.api.VIFs[ev.pub_VIF.value], MatchesXenServerVIF(
            device="0", VM=vm.xsref, network=xsh.net['eth0']))
        assert_that(xsh.api.VIFs[ev.prv_VIF.value], MatchesXenServerVIF(
            device="1", VM=vm.xsref, network=xsh.net['eth1']))

        # The VM should be started.
        assert xsh.api.VM_operations == [(vm.xsref, "start")]


@pytest.mark.django_db
class TestUpdateVms(object):
    """
    Test xenserver.tasks.updateVms task.
    """

    def test_no_servers(self, xs_helper, task_catcher):
        """
        Nothing to do if we have no servers.
        """
        us_calls = task_catcher.catch_updateServer()
        apply_task(tasks.updateVms)
        assert us_calls == []

    def test_one_server(self, xs_helper, task_catcher):
        """
        A single server will be updated.
        """
        xs_helper.new_host('xs01.local')
        us_calls = task_catcher.catch_updateServer()
        apply_task(tasks.updateVms)
        assert us_calls == ['xs01.local']

    def test_three_servers(self, xs_helper, task_catcher):
        """
        Multiple servers will be updated.
        """
        xs_helper.new_host('xs01.local')
        xs_helper.new_host('xs02.local')
        xs_helper.new_host('xs03.local')
        us_calls = task_catcher.catch_updateServer()
        apply_task(tasks.updateVms)
        assert sorted(us_calls) == ['xs01.local', 'xs02.local', 'xs03.local']


@pytest.mark.django_db
class TestUpdateServer(object):
    """
    Test xenserver.tasks.updateServer task.
    """

    def test_first_run(self, xs_helper, task_catcher):
        """
        The first run of updateServer() after a new host is added will update
        the two fields that reflect resource usage.
        """
        _, xs = xs_helper.new_host('xs01.local')
        uv_calls = task_catcher.catch_updateVm()
        xs01before = xs_helper.get_db_xenserver_dict('xs01.local')
        apply_task(tasks.updateServer, [xs])
        xs01after = xs_helper.get_db_xenserver_dict('xs01.local')
        # Two fields have changed.
        assert xs01before.pop('mem_free') != xs01after.pop('mem_free')
        assert xs01before.pop('cpu_util') != xs01after.pop('cpu_util')
        # All the others are the same.
        assert xs01before == xs01after
        assert uv_calls == []

    def test_one_vm(self, xs_helper, task_catcher):
        """
        If a server has a single VM running on it, we schedule a single
        updateVm task.
        """
        _, xs = xs_helper.new_host('xs01.local')
        vm = xs_helper.new_vm(xs, 'vm01.local')
        uv_calls = task_catcher.catch_updateVm()

        apply_task(tasks.updateServer, [xs])
        assert_that(uv_calls, MatchesSetOfLists([
            ('xs01.local', vm.xsref, MatchesVMNamed('vm01.local'))]))

    def test_two_vms(self, xs_helper, task_catcher):
        """
        If a server has two VMs running on it, we schedule an updateVm task for
        each.
        """
        _, xs = xs_helper.new_host('xs01.local')
        vm01 = xs_helper.new_vm(xs, 'vm01.local')
        vm02 = xs_helper.new_vm(xs, 'vm02.local')
        uv_calls = task_catcher.catch_updateVm()

        apply_task(tasks.updateServer, [xs])
        assert_that(uv_calls, MatchesSetOfLists([
            ('xs01.local', vm01.xsref, MatchesVMNamed('vm01.local')),
            ('xs01.local', vm02.xsref, MatchesVMNamed('vm02.local')),
        ]))


@pytest.mark.django_db
class TestUpdateVm(object):
    """
    Test xenserver.tasks.updateVm task.
    """

    def test_first_run(self, xs_helper, task_catcher):
        """
        The first run of updateVm() after a new VM is provisioned will update
        the uuid field.
        """
        xsh, xs = xs_helper.new_host('xs01.local')
        vm = xs_helper.new_vm(xs, 'vm01.local')
        vm01before = xs_helper.get_db_xenvm_dict('vm01.local')
        vmobj = xsh.get_session().xenapi.VM.get_record(vm.xsref)
        apply_task(tasks.updateVm, [xs, vm.xsref, vmobj])
        vm01after = xs_helper.get_db_xenvm_dict('vm01.local')
        # One field has changed.
        assert vm01before.pop('uuid') != vm01after.pop('uuid')
        # All the others are the same.
        assert vm01before == vm01after
