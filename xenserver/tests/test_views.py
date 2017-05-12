"""
Some quick and dirty tests for a very small subset of the code.
"""

from django.core.urlresolvers import reverse
import pytest
from testtools.assertions import assert_that
from testtools.matchers import Always, MatchesListwise

from xenserver.models import Addresses, XenVM
from xenserver.tests.helpers import DEFAULT_GATEWAY
from xenserver.tests.matchers import listmatcher


@pytest.mark.django_db
class TestProvision(object):

    def test_provision_simple(self, task_catcher, xs_helper, admin_client):
        """
        We can create a new VM using mostly default values.
        """
        createvm_calls = task_catcher.catch_create_vm()
        _, xs = xs_helper.new_host("xs01.local")
        templ = xs_helper.db_template("default")

        assert list(XenVM.objects.all()) == []
        assert list(Addresses.objects.all()) == []

        # Make the request.
        resp = admin_client.post(reverse('provision'), {
            "hostname": "foo.example.com",
            "template": templ.pk,
            "group": xs_helper.db_project("fooproj").pk,
        }, follow=True)
        assert resp.status_code == 200

        # Make sure we did the right things.
        [addr] = Addresses.objects.all()
        [vm] = XenVM.objects.all()

        assert_that(createvm_calls, MatchesListwise([listmatcher([
            vm, xs, templ, "foo", "example.com", addr.ip,
            "255.255.255.0", DEFAULT_GATEWAY, Always(), []])]))

    def test_provision_second_vif(self, task_catcher, xs_helper, admin_client):
        """
        We can create a new VM using mostly default values.
        """
        createvm_calls = task_catcher.catch_create_vm()
        _, xs = xs_helper.new_host("xs01.local")
        templ = xs_helper.db_template("default")

        assert list(XenVM.objects.all()) == []
        assert list(Addresses.objects.all()) == []

        # Make the request.
        resp = admin_client.post(reverse('provision'), {
            "hostname": "foo.example.com",
            "template": templ.pk,
            "group": xs_helper.db_project("fooproj").pk,
            "extra_network_bridges": "xenbr1",
        }, follow=True)
        assert resp.status_code == 200

        # Make sure we did the right things.
        [addr] = Addresses.objects.all()
        [vm] = XenVM.objects.all()

        assert_that(createvm_calls, MatchesListwise([listmatcher([
            vm, xs, templ, "foo", "example.com", addr.ip,
            "255.255.255.0", DEFAULT_GATEWAY, Always(), ["xenbr1"]])]))
