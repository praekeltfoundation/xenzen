"""
Some quick and dirty tests for a very small subset of the code.
"""

from django.core.urlresolvers import reverse
import pytest

from xenserver.models import (
    Addresses, AddressPool, Project, Template, XenServer, XenVM, Zone)
from xenserver import tasks
from xenserver.tests.matchers import ANY_VALUE


@pytest.mark.django_db
class TestProvision(object):
    def setup_template(self, name, cores=1, memory=2048, diskspace=10240,
                       iso="installer.iso"):
        return Template.objects.create(
            name=name, cores=cores, memory=memory, diskspace=diskspace,
            iso=iso)

    def setup_project(self, name):
        return Project.objects.create(name=name)

    def setup_server(self, hostname):
        zone = Zone.objects.create(name="foozone")
        AddressPool.objects.create(
            subnet="10.0.0.0/24", gateway="10.1.2.3", zone=zone, version=4)
        mem = 64*1024*1204*1024
        return XenServer.objects.create(
            hostname=hostname, username="u", password="p", zone=zone,
            memory=mem, mem_free=mem)

    def test_provision_simple(self, monkeypatch, settings, admin_client):
        """
        We can create a new VM using mostly default values.
        """
        createvm_calls = []
        monkeypatch.setattr(tasks, 'getSession', lambda *a, **kw: "session")
        monkeypatch.setattr(
            tasks, '_create_vm', lambda *a: createvm_calls.append(a))
        settings.CELERY_ALWAYS_EAGER = True

        self.setup_server("srv.example.com")
        templ = self.setup_template("footempl")
        proj = self.setup_project("fooproj")

        assert list(XenVM.objects.all()) == []
        assert list(Addresses.objects.all()) == []

        # Make the request.
        resp = admin_client.post(reverse('provision'), {
            "hostname": "foo.example.com",
            "template": templ.pk,
            "group": proj.pk,
        }, follow=True)
        assert resp.status_code == 200

        # Make sure we did the right things.
        [addr] = Addresses.objects.all()
        [vm] = XenVM.objects.all()

        assert [(
            "session", vm, templ, "foo", "example.com", addr.ip,
            "255.255.255.0", "10.1.2.3", ANY_VALUE, [],
        )] == createvm_calls

    def test_provision_second_vif(self, monkeypatch, settings, admin_client):
        """
        We can create a new VM using mostly default values.
        """
        createvm_calls = []
        monkeypatch.setattr(tasks, 'getSession', lambda *a, **kw: "session")
        monkeypatch.setattr(
            tasks, '_create_vm', lambda *a: createvm_calls.append(a))
        settings.CELERY_ALWAYS_EAGER = True

        self.setup_server("srv.example.com")
        templ = self.setup_template("footempl")
        proj = self.setup_project("fooproj")

        assert list(XenVM.objects.all()) == []
        assert list(Addresses.objects.all()) == []

        # Make the request.
        resp = admin_client.post(reverse('provision'), {
            "hostname": "foo.example.com",
            "template": templ.pk,
            "group": proj.pk,
            "extra_network_bridges": "xenbr1",
        }, follow=True)
        assert resp.status_code == 200

        # Make sure we did the right things.
        [addr] = Addresses.objects.all()
        [vm] = XenVM.objects.all()

        assert [(
            "session", vm, templ, "foo", "example.com", addr.ip,
            "255.255.255.0", "10.1.2.3", ANY_VALUE, ["xenbr1"],
        )] == createvm_calls
