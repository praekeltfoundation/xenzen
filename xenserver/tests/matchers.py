"""
Some helpers for testing XenServer stuff.
"""

from copy import deepcopy

from testtools.matchers import (
    Always, ContainsDict, Equals, MatchesDict, MatchesListwise,
    MatchesSetwise, Never)


class ExtractValue(object):
    """
    A matcher that will remember the first value it's compared to and match
    against that for all subsequent comparisons.
    """
    def __init__(self, name):
        self.name = name
        self.matched = False
        self.value = None

    def __str__(self):
        val = "=[%s]" % (self.value,) if self.matched else ""
        return "ExtractValue(%s)%s" % (self.name, val)

    def match(self, actual):
        if self.matched:
            return Equals(self.value).match(actual)
        else:
            self.matched = True
            self.value = actual
            return None


class ExtractValues(object):
    """
    A container for working with multiple extracted values more easily.
    """
    def __init__(self, *names):
        for name in names:
            setattr(self, name, ExtractValue(name))

    def values(self, *names):
        return [getattr(self, name).value for name in names]


def mkmatcher(x):
    return x if hasattr(x, 'match') else Equals(x)


def dictmatcher(d):
    return MatchesDict({k: mkmatcher(v) for k, v in d.items()})


def listmatcher(l, first_only=False):
    return MatchesListwise([mkmatcher(v) for v in l], first_only=first_only)


def MatchesSetOfLists(list_of_tuples):
    return MatchesSetwise(*[
        listmatcher(t, first_only=True)for t in list_of_tuples])


def MatchesVMNamed(name):
    return ContainsDict({'name_label': Equals(name)})


class BaseXenServerMatcher(object):
    """
    A base matcher for XenServer objects.
    """
    default_fields = None

    def __init__(self, **fields):
        self.fields = fields
        self.expected_fields = deepcopy(self.default_fields)
        self.expected_fields.update(self.fields)
        self.matcher = dictmatcher(self.expected_fields)

    def match(self, other):
        return self.matcher.match(other)

    def __str__(self):
        return "%s(**%r)" % (type(self).__name__, self.expected_fields)


class MatchesXenServerVM(BaseXenServerMatcher):
    """
    A matcher for a XenServer VM object.
    """
    default_fields = {
        'name_label': Never(),
        'name_description': '',
        'user_version': '1',
        'affinity': '',
        'is_a_template': False,
        'auto_power_on': False,
        'memory_static_max': Always(),
        'memory_static_min': '536870912',
        'memory_dynamic_max': Always(),
        'memory_dynamic_min': '536870912',
        'VCPUs_max': '1',
        'VCPUs_at_startup': '1',
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
        'platform': {
            'nx': 'true',
            'apic': 'true',
            'viridian': 'true',
            'pae': 'true',
            'acpi': '1',
        },
        'PCI_bus': '',
        'other_config': dictmatcher({
            'auto_poweron': 'true',
            'mac_seed': Always(),
            'install-distro': 'debianlike',
            'base_template_name': 'Ubuntu Precise Pangolin 12.04 (64-bit)',
            'install-arch': 'amd64',
            'install-methods': 'cdrom,http,ftp',
            'install-repository': 'cdrom',
            'debian-release': 'precise',
            'linux_template': 'true'
        }),
        'recommendations': '',
        'PV_args': ' -- quiet console=hvc0',
        'suspend_SR': Never(),
    }


class MatchesXenServerVIF(BaseXenServerMatcher):
    """
    A matcher for a XenServer VIF object.
    """
    default_fields = {
        'device': Never(),
        'network': Never(),
        'VM': Never(),
        'MAC': '',
        'MTU': '1500',
        'qos_algorithm_type': '',
        'qos_algorithm_params': {},
        'other_config': {}
    }
