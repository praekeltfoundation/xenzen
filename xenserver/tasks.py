import json
import time
import urllib2
from uuid import uuid4

from celery import task
from lxml import etree

import xenapi
from xenserver import iputil
from xenserver.models import (
    Addresses, AddressPool, XenMetrics, XenServer, XenVM)


def getSession(hostname, username, password):
    url = 'https://%s:443/' % (hostname)
    # First acquire a valid session by logging in:
    session = xenapi.Session(url)
    session.xenapi.login_with_password(username, password)

    return session


def getHostMetrics(session, hostname):
    t = time.time()-86400

    uri = 'http://%s/rrd_updates?session_id=%s&start=%s&host=true' % (
        hostname, session._session, int(t))

    u = urllib2.urlopen(uri)

    tree = etree.parse(u)

    rows = tree.xpath('/xport/data/row')

    legend = tree.xpath('/xport/meta/legend/entry')

    items = {}
    keys = []

    for i, l in enumerate(legend):
        key = l.text
        items[key] = []
        keys.append(key)

    cpu_all = []
    dhash = {}
    ts = []

    for r in rows:
        t = r.xpath('t')[0].text
        ts.append(int(t))

        values = r.xpath('v')
        for k, v in zip(keys, values):
            cf, rt, oid, key = k.split(':')
            if cf == 'AVERAGE':
                if rt == 'host' and key != 'cpu_avg' and key.startswith('cpu'):
                    if v.text == 'NaN':
                        continue
                    cpu_all.append(float(v.text))

                if rt == 'vm':
                    if not oid in dhash:
                        dhash[oid] = {}

                    if not key in dhash[oid]:
                        dhash[oid][key] = []

                    if v.text == 'NaN':
                        dhash[oid][key].append(None)
                    else:
                        dhash[oid][key].append(float(v.text))

    cpu_host = int((sum(cpu_all)/len(cpu_all))*100)
    return cpu_host, ts, dhash


@task(time_limit=60)
def shutdown_vm(vm):
    xenserver = vm.xenserver
    session = getSession(
        xenserver.hostname, xenserver.username, xenserver.password)

    logger = shutdown_vm.get_logger()
    logger.info("Stopping %s on %s" % (vm.name, xenserver.hostname))

    session.xenapi.VM.shutdown(vm.xsref)
    session.xenapi.session.logout()


@task(time_limit=60)
def reboot_vm(vm):
    xenserver = vm.xenserver
    session = getSession(
        xenserver.hostname, xenserver.username, xenserver.password)

    logger = reboot_vm.get_logger()
    logger.info("Rebooting %s on %s" % (vm.name, xenserver.hostname))

    session.xenapi.VM.hard_reboot(vm.xsref)
    session.xenapi.session.logout()


@task(time_limit=60)
def start_vm(vm):
    xenserver = vm.xenserver
    session = getSession(
        xenserver.hostname, xenserver.username, xenserver.password)

    logger = start_vm.get_logger()
    logger.info("Starting %s on %s" % (vm.name, xenserver.hostname))

    session.xenapi.VM.start(vm.xsref, False, True)
    session.xenapi.session.logout()


@task(time_limit=120)
def destroy_vm(vm):
    xenserver = vm.xenserver
    session = getSession(
        xenserver.hostname, xenserver.username, xenserver.password)

    logger = destroy_vm.get_logger()
    logger.info("Terminating %s on %s" % (vm.name, xenserver.hostname))

    vmobj = session.xenapi.VM.get_record(vm.xsref)

    try:
        session.xenapi.VM.hard_shutdown(vm.xsref)
    except:
        pass

    # Get attached VBDs and destroy any attached disk VDIs
    vbds = vmobj['VBDs']
    for vbref in vbds:
        vbd = session.xenapi.VBD.get_record(vbref)
        if vbd['type'] == 'Disk':
            vdi = vbd['VDI']
            session.xenapi.VDI.destroy(vdi)

    session.xenapi.VM.destroy(vm.xsref)
    session.xenapi.session.logout()

    vm.delete()


def updateAddress(server, vm, ip, pool=None):
    ip_int = iputil.stoip(ip)

    if not pool:
        for p in AddressPool.objects.filter(zone=server.zone):
            ipnl, first, last, cidr = iputil.ipcalc(p.subnet)
            if (ip_int >= first) and (ip_int <= last):
                pool = p

    if pool:
        try:
            addr = Addresses.objects.get(ip_int=ip_int)
            addr.vm = vm
        except:
            addr = Addresses.objects.create(
                ip=ip,
                ip_int=ip_int,
                version=':' in ip and 6 or 4,
                vm=vm,
                pool=pool
            )

        addr.save()


@task(time_limit=60)
def updateVm(xenserver, vmref, vmobj):
    if (not vmobj['is_a_template']) and (not vmobj['is_control_domain']):
        try:
            session = getSession(
                xenserver.hostname, xenserver.username, xenserver.password)
            netip = session.xenapi.VM_guest_metrics.get_record(
                        vmobj['guest_metrics']
                    )['networks']['0/ip']
            session.xenapi.session.logout()
        except:
            netip = ''

        name = vmobj['name_label']

        try:
            vm = XenVM.objects.get(xenserver=xenserver, name=name)
            vm.name = name
            vm.status = vmobj['power_state']
            vm.sockets = int(vmobj['VCPUs_max'])
            vm.memory = int(vmobj['memory_static_max']) / 1048576
            vm.uuid = vmobj['uuid']
            vm.xenserver = xenserver
            vm.xsref = vmref

            if netip:
                vm.ip = netip

        except XenVM.DoesNotExist:
            vm = XenVM.objects.create(
                xsref=vmref,
                uuid=vmobj['uuid'],
                name=name,
                status=vmobj['power_state'],
                sockets=int(vmobj['VCPUs_max']),
                memory=int(vmobj['memory_static_max']) / 1048576,
                xenserver=xenserver,
                ip=netip
            )

        vm.save()

        # Update the address table
        if netip:
            try:
                updateAddress(xenserver, vm, netip)
            except:
                pass


@task(time_limit=60)
def updateServer(xenserver):
    session = getSession(
        xenserver.hostname, xenserver.username, xenserver.password)

    # get server info
    host = session.xenapi.host.get_all()[0]
    host_info = session.xenapi.host.get_record(host)
    cores = int(host_info['cpu_info']['cpu_count'])

    xenserver.cores = cores

    metrics = session.xenapi.host_metrics.get_record(
        session.xenapi.host.get_metrics(host)
    )
    memory = metrics['memory_total']
    mem_free = metrics['memory_free']

    xenserver.memory = int(memory) / 1048576
    xenserver.mem_free = int(mem_free) / 1048576

    try:
        xenserver.cpu_util, ts, vmstats = getHostMetrics(
            session, xenserver.hostname)
    except:
        xenserver.cpu_util = 0
        vmstats = {}
        ts = []

    xenserver.save()

    # List all the VM objects
    #allvms = session.xenapi.host.get_resident_VMs(host)
    allvms = session.xenapi.VM.get_all_records()
    vmrefs = allvms.keys()

    session.xenapi.session.logout()

    # Update all the vm info
    for vmref, vmobj in allvms.items():
        updateVm.delay(xenserver, vmref, vmobj)

    # Prevent cleaning an unreferenced VM
    for vm in XenVM.objects.filter(xsref__startswith='TEMPREF'):
        vmrefs.append(vm.xsref)

    # Purge lost VM's
    lost = XenVM.objects.filter(
        xenserver=xenserver).exclude(xsref__in=vmrefs).delete()

    # Update vm metrics
    for vm, stats in vmstats.items():
        # Get VM
        try:
            vmobj = XenVM.objects.get(uuid=vm)
        except:
            continue

        for key, stat in stats.items():
            try:
                metric = XenMetrics.objects.get(vm=vmobj, key=key)
                metric.timeblob = json.dumps(ts)
                metric.datablob = json.dumps(stat)
            except:
                metric = XenMetrics.objects.create(
                    vm=vmobj,
                    key=key,
                    timeblob=json.dumps(ts),
                    datablob=json.dumps(stat)
                )
            metric.save()


@task(time_limit=60)
def updateVms():
    servers = XenServer.objects.all()
    for xenserver in servers:
        updateServer.delay(xenserver)


@task(time_limit=120)
def complete_vm(vm):
    # Hook task for post provisioning cleanup
    xenserver = vm.xenserver

    session = getSession(
        xenserver.hostname, xenserver.username, xenserver.password)

    rec = session.xenapi.VM.get_record(vm.xsref)

    vbds = rec['VBDs']

    for vbd in vbds:
        vbrec = session.xenapi.VBD.get_record(vbd)
        if vbrec['type'] == 'CD' and not vbrec['empty']:
            session.xenapi.VBD.eject(vbd)


@task(time_limit=120)
def create_vm(vm, xenserver, template, name, domain, ip, subnet, gateway,
              preseed_url, extra_network_bridges=()):
    session = getSession(
        xenserver.hostname, xenserver.username, xenserver.password)
    return _create_vm(
        session, vm, template, name, domain, ip, subnet, gateway, preseed_url,
        extra_network_bridges)


def _create_vm(session, vm, template, name, domain, ip, subnet, gateway,
               preseed_url, extra_network_bridges):
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

    extra_networks = []
    xen_networks = session.xenapi.network.get_all()
    for br in extra_network_bridges:
        found = False
        for net in xen_networks:
            r = session.xenapi.network.get_record(net)
            if r['bridge'] == br:
                extra_networks.append(net)
                found = True
                break
        if not found:
            raise NetworkError('Unable to locate extra network')

    platfrm = {
        'nx': 'true',
        'apic': 'true',
        'viridian': 'true',
        'pae': 'true',
        'acpi': '1'
    }

    boot_params = template.bootopts % {
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
        'memory_static_min': '536870912',
        'memory_dynamic_max': mem_bytes,
        'memory_dynamic_min': '536870912',
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
            'auto_poweron': 'true',
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
        'PV_args': '%s -- quiet console=hvc0' % boot_params,
        'suspend_SR': local_sr
    }

    # Create virtual machine
    try:
        VM_ref = session.xenapi.VM.create(vmprop)
    except Exception, e:
        vm.delete()
        raise e
        return

    # Update our OpaqueRef
    vm.xsref = VM_ref
    vm.save()

    vif = {
        'device': '0',
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

    devicenum = 0
    for extra_network in extra_networks:
        devicenum += 1
        session.xenapi.VIF.create({
            'device': str(devicenum),
            'network': extra_network,
            'VM': VM_ref,
            'MAC': '',
            'MTU': '1500',
            'qos_algorithm_type': '',
            'qos_algorithm_params': {},
            'other_config': {},
        })

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
    vdi_ref = session.xenapi.VDI.create(vdisk)

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
    vbdref1 = session.xenapi.VBD.create(visoconnect)

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
    vbdref = session.xenapi.VBD.create(vbdconnect)

    # Boot the VM up
    session.xenapi.VM.start(VM_ref, False, False)

    session.xenapi.session.logout()
