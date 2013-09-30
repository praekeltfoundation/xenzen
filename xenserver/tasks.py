from celery import task
import os
import sys
import subprocess
import xenapi

from xenserver.models import XenServer, XenVM

def getSession(hostname, username, password):
    url = "https://%s:443/" % (hostname)
    # First acquire a valid session by logging in:
    session = xenapi.Session(url)
    session.xenapi.login_with_password(username, password)

    return session

def getVms(session):

    return vms

@task()
def updateVms():
    servers = XenServer.objects.all()

    for xenserver in servers:
        session = getSession(xenserver.hostname,
            xenserver.username, xenserver.password)

        # get server info 
        host = session.xenapi.host.get_all()[0]
        host_info = session.xenapi.host.get_record(host)
        cores = int(host_info['cpu_info']['cpu_count'])

        xenserver.cores = cores

        metrics = session.xenapi.host.get_metrics(host)
        memory = session.xenapi.host_metrics.get_record(metrics)['memory_total']
        xenserver.memory = int(memory) / 1048576

        xenserver.save()

        # List all the VM objects
        allvms = session.xenapi.VM.get_all()

        for vmref in allvms:
            v = session.xenapi.VM.get_record(vmref)

            try:
                netip = session.xenapi.VM_guest_metrics.get_record(
                    v['guest_metrics'])['networks']['0/ip']
            except:
                netip = ''

            if (not v["is_a_template"]) and (not v["is_control_domain"]):
                try:
                    vmobj = XenVM.objects.get(xsref=vmref)
                    vmobj.name = v['name_label']
                    vmobj.status = v['power_state']
                    vmobj.sockets = int(v['VCPUs_max'])
                    vmobj.memory = int(v['memory_static_max']) / 1048576
                    vmobj.xenserver = xenserver
                    vmobj.ip = netip

                except XenVM.DoesNotExist:
                    vmobj = XenVM.objects.create(
                        xsref=vmref,
                        name=v['name_label'],
                        status=v['power_state'],
                        sockets=int(v['VCPUs_max']),
                        memory=int(v['memory_static_max']) / 1048576,
                        xenserver=xenserver,
                        ip=netip
                    )

                vmobj.save()

        session.xenapi.session.logout()

@task()
def create_vm(name):
    # something here
    pass
