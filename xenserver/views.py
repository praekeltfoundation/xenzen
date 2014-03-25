from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.forms import ValidationError

from xenserver.models import XenServer, XenVM, Template, AuditLog, Zone
from xenserver import forms, tasks, iputil

import hashlib
import uuid
import time
import random
import urlparse
from operator import itemgetter

from celery.task.control import revoke


def log_action(user, severity, message):
    log = AuditLog.objects.create(username=user, severity=severity, 
        message=message)
    log.save()

@login_required
def index(request):
    vms = XenVM.objects.all().order_by('name')


    return render(request, "index.html", {
        'vms': vms
    })

@login_required
def server_index(request):

    servers = XenServer.objects.all().order_by('hostname')
    templates = Template.objects.all().order_by('-memory')

    stacks = []

    slack = {}

    for t in templates:
        slack[t] = 0

    global_free = 1
    global_total = 1
    global_cores = 1
    global_vmcores = 1

    for server in servers:
        vms = server.xenvm_set.all().order_by('name')

        used_memory = sum([vm.memory for vm in vms])
        mem_total = server.memory - 2800
        if not mem_total:
            # Prevent a divide by zero
            mem_total = 1 
        mem_util = (used_memory/float(mem_total))*100
        mem_free = mem_total - used_memory

        vmcores = sum([vm.sockets for vm in vms])
        xscores = server.cores

        global_cores += xscores
        global_vmcores += vmcores
        global_free += mem_free
        global_total += mem_total

        stacks.append({
            'id': server.id,
            'hostname': server.hostname,
            'vms': vms, 
            'mem_util': mem_util,
            'mem_total': mem_total,
            'mem_used': used_memory,
            'cores': xscores,
            'coresused': vmcores
        })

        for t in templates:
            if t.memory < mem_free:
                count = mem_free / t.memory
                slack[t] += count

    return render(request, "servers/index.html", {
        'servers': stacks, 
        'template_slack': slack.items(),
        'global': {
            'cores': global_cores,
            'freemem': '{:,}'.format(global_free),
            'totalmem': '{:,}'.format(global_total),
            'vmcores': global_vmcores,
            'corecontend': '%0.2f' % (global_vmcores/float(global_cores))
        }
    })

@login_required
def accounts_profile(request):
    if request.method == "POST":
        form = forms.UserForm(request.POST, instance=request.user)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('home')
    else:
        form = forms.UserForm(instance=request.user)

    return render(request, "accounts_profile.html", {
        'form': form
    })

@login_required
def log_index(request):
    logs = AuditLog.objects.all().order_by('-time')

    return render(request, "log_index.html", {
        'logs': logs
    })

@login_required
def template_index(request):

    templates = Template.objects.all().order_by('memory')

    return render(request, "templates/index.html", {
        'templates': templates
    })

@login_required
def template_create(request):
    if not request.user.is_superuser:
        return redirect('template_index')

    if request.method == "POST":
        form = forms.TemplateForm(request.POST)
        if form.is_valid():
            template = form.save(commit=False)
            template.save()
            log_action(request.user, 3, "Created template %s" % template.name)
            return redirect('template_index')

    else:
        form = forms.TemplateForm()

    return render(request, 'templates/create_edit.html', {
        'form': form
    })

@login_required
def template_edit(request, id):
    if not request.user.is_superuser:
        return redirect('home')

    template = Template.objects.get(id=id)
    if request.method == "POST":
        form = forms.TemplateForm(request.POST, instance=template)

        if form.is_valid():
            template = form.save(commit=False)
            template.save()

            log_action(request.user, 3, "Edit template %s" % template.name)

            return redirect('template_index')

    else:
        form = forms.TemplateForm(instance=template)
    d = {
        'form': form, 
        'template': template
    }

    return render(request, 'templates/create_edit.html', d)

@login_required
def zone_index(request):
    zones = Zone.objects.all().order_by('name')

    return render(request, "zones/index.html", {
        'zones': zones
    })

@login_required
def zone_edit(request, id):
    if not request.user.is_superuser:
        return redirect('home')

    zone = Zone.objects.get(id=id)

    if request.method == "POST":
        form = forms.ZoneForm(request.POST, instance=zone)

        if form.is_valid():
            zone = form.save(commit=False)
            zone.save()

            log_action(request.user, 3, "Edited zone %s" % zone.name)
            return redirect('zone_index')

    else:
        form = forms.ZoneForm(instance=zone)

    return render(request, 'zones/create_edit.html', {
        'form': form, 
        'zone': zone
    })

@login_required
def zone_create(request):
    if not request.user.is_superuser:
        return redirect('index')

    if request.method == "POST":
        form = forms.ZoneForm(request.POST)
        if form.is_valid():
            zone = form.save(commit=False)
            zone.save()

            log_action(request.user, 2, "Created zone %s" % zone.name)
            return redirect('zone_index')
    else:
        form = forms.ZoneForm()

    return render(request, 'zones/create_edit.html', {
        'form': form
    })

@login_required
def zone_view(request, id):
    zone = Zone.objects.get(id=id)
    servers = XenServer.objects.filter(zone=zone).order_by('hostname')

    return render(request, "zones/view.html", {
        'servers': servers,
        'zone': zone
    })


@login_required
def server_view(request, id):
    server = XenServer.objects.get(id=id)

    vms = server.xenvm_set.all().order_by('name')
    used_addresses = [vm.ip for vm in vms if vm.ip]

    return render(request, 'servers/view.html', {
        'server': server, 
        'vms': vms, 
    })

@login_required
def server_create(request):
    if not request.user.is_superuser:
        return redirect('server_index')

    if request.method == "POST":
        form = forms.XenServerForm(request.POST)
        if form.is_valid():
            server = form.save(commit=False)
            server.save()

            log_action(request.user, 3, "Added server %s" % server.hostname)
            return redirect('server_index')

    else:
        form = forms.XenServerForm()

    return render(request, 'servers/create_edit.html', {
        'form': form
    })

@login_required
def server_edit(request, id):
    if not request.user.is_superuser:
        return redirect('home')

    server = XenServer.objects.get(id=id)
    if request.method == "POST":
        form = forms.XenServerForm(request.POST, instance=server)

        if form.is_valid():
            server = form.save(commit=False)
            server.save()

            log_action(request.user, 3, "Edited server %s" % server.hostname)
            return redirect('server_index')

    else:
        form = forms.XenServerForm(instance=server)
    d = {
        'form': form, 
        'server': server
    }

    return render(request, 'servers/create_edit.html', d)

@login_required
def start_vm(request, id):
    if not request.user.is_superuser:
        return redirect('home')

    vm = XenVM.objects.get(id=id)

    if vm.xsref:
        vm.status = 'Starting'
        vm.save()

        tasks.start_vm.delay(vm)

        log_action(request.user, 3, "Started VM %s on %s" % (
            vm.name,
            vm.xenserver.hostname
        ))

    return redirect('home')

@login_required
def stop_vm(request, id):
    if not request.user.is_superuser:
        return redirect('home')

    vm = XenVM.objects.get(id=id)

    if vm.xsref:
        vm.status = 'Stopping'
        vm.save()

        tasks.shutdown_vm.delay(vm)

        log_action(request.user, 3, "Shutdown VM %s on %s" % (
            vm.name,
            vm.xenserver.hostname
        ))

    return redirect('home')

@login_required
def reboot_vm(request, id):
    if not request.user.is_superuser:
        return redirect('home')

    vm = XenVM.objects.get(id=id)

    if vm.xsref:
        vm.status = 'Rebooting'
        vm.save()

        tasks.reboot_vm.delay(vm)

        log_action(request.user, 3, "Rebooted VM %s on %s" % (
            vm.name,
            vm.xenserver.hostname
        ))

    return redirect('home')

@login_required
def terminate_vm(request, id):
    if not request.user.is_superuser:
        return redirect('home')

    vm = XenVM.objects.get(id=id)

    if vm.xsref:
        vm.status = 'Terminating'
        vm.save()

        tasks.destroy_vm.delay(vm)
        log_action(request.user, 3, "Terminated VM %s on %s" % (
            vm.name,
            vm.xenserver.hostname
        ))

    return redirect('home')

@login_required
def provision(request):
    if request.method == "POST":
        form = forms.ProvisionForm(request.POST)
        if form.is_valid():
            provision = form.cleaned_data
            server = provision['server']
            zone = provision['zone']
            template = provision['template']
            hostname = provision['hostname']
            host, domain = hostname.split('.', 1)

            # Server autoselect
            if not server:
                if zone:
                    servers = XenServer.objects.filter(zone=zone).order_by('hostname')
                else:
                    servers = XenServer.objects.all().order_by('hostname')

                hosts = []

                for s in servers:
                    vms = s.xenvm_set.all().order_by('name')

                    used_memory = sum([vm.memory for vm in vms])
                    used_cores = sum([vm.sockets for vm in vms])
                    mem_total = s.memory
                    if not mem_total:
                        # Prevent a divide by zero
                        mem_total = 1 

                    free = mem_total - used_memory
                    if free > (template.memory + 2800):
                        hosts.append((s, free, s.cores - used_cores))

                # Pick the least utilised server
                server = sorted(hosts, key=itemgetter(2,1))[0][0]


            if provision['ipaddress']:
                cidr = provision['ipaddress']
                subnet = iputil.getSubnet(cidr)

                ip = cidr.split('/')[0]
                gateway = iputil.getGateway(subnet)
                netmask = iputil.getNetmask(subnet)
            else:
                # Find the first free IP address
                vms = server.xenvm_set.all()
                used_addresses = [vm.ip for vm in vms if vm.ip]
                ip = iputil.firstRemaining(server.subnet, used_addresses)
                gateway = iputil.getGateway(server.subnet)
                netmask = iputil.getNetmask(server.subnet)

            # Get a preseed URL
            url = urlparse.urljoin(request.build_absolute_uri(),
                reverse('get_preseed', kwargs={'id':template.id}))

            vmobj = XenVM.objects.create(
                xsref='TEMPREF'+uuid.uuid1().hex,
                name=hostname,
                status='Provisioning',
                sockets=template.cores,
                memory=template.memory,
                xenserver=server,
                ip=ip
            )
            vmobj.save()

            # Send provisioning to celery
            task = tasks.create_vm.delay(
                server, template, host, domain, ip, netmask, gateway, url)

            log_action(request.user, 3, "Provisioned VM %s on %s" % (
                hostname,
                server.hostname
            ))

            return redirect('home')
    else:
        form = forms.ProvisionForm()

    return render(request, 'provision.html', {
        'form': form
    })

def get_preseed(request, id):
    template = Template.objects.get(id=id)

    return HttpResponse(template.preseed, content_type="text/plain")
