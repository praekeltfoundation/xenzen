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
def create_vm(xenserver, template, name, domain, ip, subnet, gateway):
    session = getSession(xenserver.hostname,
            xenserver.username, xenserver.password)
    storage = session.xenapi.SR.get_all()

    ubuntu_vdi = ''
    local_sr = ''

    for s in storage:
        store_record = session.xenapi.SR.get_record(s)
        if store_record['type'] == 'iso':
            vdis = store_record['VDIs']
            for vdi in vdis:
                vr = session.xenapi.VDI.get_record(vdi)
                # XXX - add Template model reference to choose ISO's and disk provision sizes etc
                if vr['name_label'] == 'ubuntu-12.04.3-server-amd64.iso':
                    ubuntu_vdi = vdi

        if store_record['name_label'] == 'Local storage':
            # Attatch local SR
            local_sr = s

    if not local_sr:
        raise StorageError('Unable to locate "Local storage" SR')

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
        "nx": "true",
        "apic": "true",
        "viridian": "true",
        "pae": "true",
        "acpi": "1"
    }

    boot_params = "debian-installer/locale=en_ZA.UTF-8 console-setup/layoutcode=us console-setup/ask_detect=false interface=eth0 netcfg/get_hostname=%(name)s netcfg/get_domain=%(domain)s netcfg/disable_autoconfig=true netcfg/get_ipaddress=%(ip)s netcfg/get_netmask=%(subnet)s netcfg/get_gateway=%(gateway)s netcfg/get_nameservers=8.8.8.8 preseed/url=http://puppet.za.prk-host.net/preseed-precise.cfg" % {
        'ip': ip, 
        'subnet': subnet, 
        'gateway': gateway, 
        'name': name, 
        'domain': domain
    },


    vmprop = {
        'name_label':name,
        'name_description':"",
        'user_version':"1",
        'affinity':"",
        'is_a_template':False,
        'auto_power_on':False,
        'memory_static_max':"1073741824",
        'memory_static_min':"1073741824",
        'memory_dynamic_max':"1073741824",
        'memory_dynamic_min':"1073741824",
        'VCPUs_max':"1",
        'VCPUs_at_startup':"1",
        'VCPUs_params':{},
        'actions_after_shutdown':"destroy",
        'actions_after_reboot':"restart",
        'actions_after_crash':"restart",
        'PV_kernel':"",
        'PV_ramdisk':"",
        'PV_bootloader':"eliloader",
        'PV_bootloader_args':"",
        'PV_legacy_args':"",
        'HVM_boot_policy':'',
        'HVM_boot_params':{},
        'platform':platfrm,
        'PCI_bus':"",
        "other_config": {
            "mac_seed": "38a679e8-7d36-216e-cf99-a2acd6cee00e",
            "install-distro": "debianlike",
            "base_template_name": "Ubuntu Precise Pangolin 12.04 (64-bit)",
            "install-arch": "amd64",
            "install-methods": "cdrom,http,ftp",
            "install-repository": "cdrom",
            "debian-release": "precise",
            "linux_template": "true"
        },
        'recommendations':"",
        'PV_args':"-- quiet console=hvc0 %s" % boot_params,
        "suspend_SR": local_sr
    }

    VM_ref=session.xenapi.VM.create(vmprop)

    vif = { 'device': '0',
            'network': network,
            'VM': VM_ref,
            'MAC': "",
            'MTU': "1500",
            "qos_algorithm_type": "",
            "qos_algorithm_params": {},
            "other_config": {}
        }

    session.xenapi.VIF.create(vif)

    vdisk = {
        'name_label' : name + ' 0',
        'name_description' : "",
        'SR' : local_sr,
        'virtual_size' : "10737418240",
        'type' : 'system',
        'sharable' : False,
        'read_only' : False,
        'other_config' : {}
    }

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
    vbdref1=session.xenapi.VBD.create(visoconnect)

    vbdconnect = {
        'VDI': vdi_ref,
        'VM': VM_ref,
        'userdevice': "0",
        'mode': 'RW',
        'type': "Disk",
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

    vbdref=session.xenapi.VBD.create(vbdconnect)

    session.xenapi.VM.start(VM_ref, False, False)

