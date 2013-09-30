from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from xenserver.models import XenServer
from xenserver import forms, tasks, iputil

import hashlib
import uuid
import time
import random
import urlparse

from celery.task.control import revoke

@login_required
def index(request):
    servers = XenServer.objects.all()

    stacks = []

    for server in servers:
        vms = server.xenvm_set.all()

        used_memory = sum([vm.memory for vm in vms])
        mem_total = server.memory
        mem_util = (used_memory/float(mem_total))*100

        stacks.append({
            'hostname': server.hostname,
            'vms': vms, 
            'mem_util': mem_util,
            'mem_total': mem_total,
            'mem_used': used_memory
        })

    return render(request, "index.html", {
        'servers': stacks
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
def server_index(request):
    servers = XenServer.objects.all()
    
    d = {'servers': servers}
    return render(request, "servers/index.html", d)

@login_required
def server_view(request, id):
    server = XenServer.objects.get(id=id)

    vms = server.xenvm_set.all()

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

            return redirect('server_index')

    else:
        form = forms.XenServerForm(instance=server)
    d = {
        'form': form, 
        'server': server
    }

    return render(request, 'servers/create_edit.html', d)

@login_required
def provision(request):
    
    if request.method == "POST":
        pass
    else:
        form = forms.ProvisionForm()

    return render(request, 'provision.html', {
        'form': form
    })



