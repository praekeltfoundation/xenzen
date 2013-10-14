from celery import task
from uuid import uuid4
import os
import sys
import subprocess
import xenapi

from xenserver.models import XenServer, XenVM

def getSession(hostname, username, password):
    url = 'https://%s:443/' % (hostname)
    # First acquire a valid session by logging in:
    session = xenapi.Session(url)
    session.xenapi.login_with_password(username, password)

    return session

def getVms(session):

    return vms

@task()
def shutdown_vm(vm):
    xenserver = vm.xenserver
    session = getSession(xenserver.hostname,
        xenserver.username, xenserver.password)

    logger = shutdown_vm.get_logger()
    logger.info("Stopping %s on %s" % (vm.name, xenserver.hostname))

    session.xenapi.VM.shutdown(vm.xsref)
    session.xenapi.session.logout()

@task()
def reboot_vm(vm):
    xenserver = vm.xenserver
    session = getSession(xenserver.hostname,
        xenserver.username, xenserver.password)

    logger = reboot_vm.get_logger()
    logger.info("Rebooting %s on %s" % (vm.name, xenserver.hostname))

    session.xenapi.VM.hard_reboot(vm.xsref)
    session.xenapi.session.logout()

@task()
def start_vm(vm):
    xenserver = vm.xenserver
    session = getSession(xenserver.hostname,
        xenserver.username, xenserver.password)

    logger = start_vm.get_logger()
    logger.info("Starting %s on %s" % (vm.name, xenserver.hostname))

    session.xenapi.VM.start(vm.xsref, False, True)
    session.xenapi.session.logout()

@task()
def destroy_vm(vm):
    xenserver = vm.xenserver
    session = getSession(xenserver.hostname,
        xenserver.username, xenserver.password)

    logger = destroy_vm.get_logger()
    logger.info("Terminating %s on %s" % (vm.name, xenserver.hostname))

    try:
        session.xenapi.VM.hard_shutdown(vm.xsref)
    except:
        pass

    session.xenapi.VM.destroy(vm.xsref)
    session.xenapi.session.logout()

    vm.delete()

@task
def updateVm(xenserver, vmref):
    session = getSession(xenserver.hostname,
        xenserver.username, xenserver.password)

    v = session.xenapi.VM.get_record(vmref)

    if (not v['is_a_template']) and (not v['is_control_domain']):
        try:
            netip = session.xenapi.VM_guest_metrics.get_record(
                v['guest_metrics'])['networks']['0/ip']
        except:
            netip = ''

        # Done with session

        name = v['name_label']

        try:
            vmobj = XenVM.objects.get(xenserver=xenserver, name=name)
            vmobj.name = v['name_label']
            vmobj.status = v['power_state']
            vmobj.sockets = int(v['VCPUs_max'])
            vmobj.memory = int(v['memory_static_max']) / 1048576
            vmobj.xenserver = xenserver
            vmobj.xsref = vmref

            if netip:
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

@task
def updateServer(xenserver):
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
    allvms = session.xenapi.host.get_resident_VMs(host)
    session.xenapi.session.logout()

    # Update all the vm info
    for vmref in allvms:
        updateVm.delay(xenserver, vmref)

    # Prevent cleaning an unreferenced VM
    allvms.append('')

    # Purge lost VM's 
    lost = XenVM.objects.filter(xenserver=xenserver).exclude(xsref__in=allvms).delete()

@task()
def updateVms():
    servers = XenServer.objects.all()
    for xenserver in servers:
        updateServer.delay(xenserver)

@task()
def create_vm(xenserver, template, name, domain, ip, subnet, gateway, preseed_url):
    session = getSession(xenserver.hostname,
            xenserver.username, xenserver.password)

    mem_bytes = str(template.memory * (1024*1024))
    cores = str(template.cores)
    disk_bytes = str(template.diskspace * (1024*1024*1024))

    storage = session.xenapi.SR.get_all()
    ubuntu_vdi = ''
    local_sr = ''
    for s in storage:
        store_record = session.xenapi.SR.get_record(s)
        if store_record['type'] == 'iso':
            vdis = store_record['VDIs']
            for vdi in vdis:
                vr = session.xenapi.VDI.get_record(vdi)
                if vr['name_label'] == template.iso:
                    ubuntu_vdi = vdi

        if store_record['name_label'] == 'Local storage':
            # Attatch local SR
            local_sr = s

    if not local_sr:
        raise StorageError("Unable to locate 'Local storage' SR")

    if not ubuntu_vdi:
        raise StorageError('Unable to locate installation source ISO')

    phys = session.xenapi.PIF.get_all()
    network = None
    for phy in phys:
        r = session.xenapi.PIF.get_record(phy)

        if r['gateway']:
            network = phy
            break

    network = session.xenapi.PIF.get_network(network)

    if not network:
        raise NetworkError('Unable to locate VIF network')

    platfrm = {
        'nx': 'true',
        'apic': 'true',
        'viridian': 'true',
        'pae': 'true',
        'acpi': '1'
    }

    boot_params = 'debian-installer/locale=en_ZA.UTF-8 console-setup/layoutcode=us console-setup/ask_detect=false interface=eth0 netcfg/get_hostname=%(name)s netcfg/get_domain=%(domain)s netcfg/disable_autoconfig=true netcfg/get_ipaddress=%(ip)s netcfg/get_netmask=%(subnet)s netcfg/get_gateway=%(gateway)s netcfg/get_nameservers=8.8.8.8 preseed/url=%(url)s' % {
        'ip': ip, 
        'subnet': subnet, 
        'gateway': gateway, 
        'name': name, 
        'domain': domain, 
        'url': preseed_url
    }

    vmname = "%s.%s" % (name, domain)

    vmprop = {
        'name_label': vmname,
        'name_description': '',
        'user_version': '1',
        'affinity': '',
        'is_a_template': False,
        'auto_power_on': False,
        'memory_static_max': mem_bytes,
        'memory_static_min': mem_bytes,
        'memory_dynamic_max': mem_bytes,
        'memory_dynamic_min': mem_bytes,
        'VCPUs_max': cores,
        'VCPUs_at_startup': cores,
        'VCPUs_params': {},
        'actions_after_shutdown': 'destroy',
        'actions_after_reboot': 'restart',
        'actions_after_crash': 'restart',
        'PV_kernel': '',
        'PV_ramdisk': '',
        'PV_bootloader': 'eliloader',
        'PV_bootloader_args': '',
        'PV_legacy_args': '',
        'HVM_boot_policy': '',
        'HVM_boot_params': {},
        'platform': platfrm,
        'PCI_bus': '',
        'other_config': {
            'mac_seed': str(uuid4()),
            'install-distro': 'debianlike',
            'base_template_name': 'Ubuntu Precise Pangolin 12.04 (64-bit)',
            'install-arch': 'amd64',
            'install-methods': 'cdrom,http,ftp',
            'install-repository': 'cdrom',
            'debian-release': 'precise',
            'linux_template': 'true'
        },
        'recommendations': '',
        'PV_args': '-- quiet console=hvc0 %s' % boot_params,
        'suspend_SR': local_sr
    }

    # Create virtual machine
    VM_ref=session.xenapi.VM.create(vmprop)

    vif = { 'device': '0',
            'network': network,
            'VM': VM_ref,
            'MAC': '',
            'MTU': '1500',
            'qos_algorithm_type': '',
            'qos_algorithm_params': {},
            'other_config': {}
        }

    # Create and attach network interface
    session.xenapi.VIF.create(vif)

    vdisk = {
        'name_label': vmname + ' 0',
        'name_description': '',
        'SR': local_sr,
        'virtual_size': disk_bytes,
        'type': 'system',
        'sharable': False,
        'read_only': False,
        'other_config': {}
    }

    # Create the VDI for our disk
    vdi_ref=session.xenapi.VDI.create(vdisk)

    visoconnect = {
        'VDI': ubuntu_vdi,
        'VM': VM_ref,
        'userdevice': '3',
        'allowed_operations': ['attach', 'eject'],
        'storage_lock': False,
        'mode': 'RO',
        'type': 'CD',
        'bootable': True,
        'unpluggable': True,
        'empty': False,
        'other_config': {},
        'qos_algorithm_type': '',
        'qos_algorithm_params': {}
    }
    # Connect the ISO device
    vbdref1=session.xenapi.VBD.create(visoconnect)

    vbdconnect = {
        'VDI': vdi_ref,
        'VM': VM_ref,
        'userdevice': '0',
        'mode': 'RW',
        'type': 'Disk',
        'bootable': False,
        'unpluggable': False,
        'device': '',
        'empty': False,
        'storage_lock': False,
        'other_config': {'owner': ''},
        'qos_algorithm_type': '',
        'qos_algorithm_params': {},
        'allowed_operations': ['attach'],
    }
    # Connect the disk VDI 
    vbdref=session.xenapi.VBD.create(vbdconnect)

    # Boot the VM up
    session.xenapi.VM.start(VM_ref, False, False)

    session.xenapi.session.logout()

