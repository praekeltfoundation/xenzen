"""
Some helpers for testing XenServer stuff.
"""

from copy import deepcopy


class NVType(object):
    """
    An object to represent a missing value.
    """
    def __repr__(self):
        return "<NO VALUE>"

    def __eq__(self, other):
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


NO_VALUE = NVType()


class AVType(object):
    """
    An object to represent any value.
    """
    def __repr__(self):
        return "<ANY VALUE>"

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return not self.__eq__(other)


ANY_VALUE = AVType()


class ExtractValue(object):
    """
    A matcher that will extract whatever value it matches.
    """
    def __init__(self, name):
        self.name = name
        self.value = NO_VALUE

    def __repr__(self):
        return "<ExtractValue %s=%r>" % (self.name, self.value)

    def __eq__(self, other):
        if self.value is not NO_VALUE:
            return self.value == other
        self.value = other
        return True

    def __ne__(self, other):
        return not self.__eq__(other)


class ExpectedXenServerObject(object):
    """
    A base matcher for XenServer objects.
    """
    default_fields = None

    def __init__(self, **fields):
        self.fields = fields
        self.expected_fields = deepcopy(self.default_fields)
        self.expected_fields.update(self.fields)

    def assertMatch(self, other):
        assert self.expected_fields == other

    def __repr__(self):
        return "<%s %r>" % (type(self).__name__, self.expected_fields)


class ExpectedXenServerVM(ExpectedXenServerObject):
    """
    A matcher for a XenServer VM object.
    """
    default_fields = {
        'name_label': NO_VALUE,
        'name_description': '',
        'user_version': '1',
        'affinity': '',
        'is_a_template': False,
        'auto_power_on': False,
        'memory_static_max': NO_VALUE,
        'memory_static_min': '536870912',
        'memory_dynamic_max': NO_VALUE,
        'memory_dynamic_min': '536870912',
        'VCPUs_max': NO_VALUE,
        'VCPUs_at_startup': NO_VALUE,
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
        'other_config': {
            'auto_poweron': 'true',
            'mac_seed': ANY_VALUE,
            'install-distro': 'debianlike',
            'base_template_name': 'Ubuntu Precise Pangolin 12.04 (64-bit)',
            'install-arch': 'amd64',
            'install-methods': 'cdrom,http,ftp',
            'install-repository': 'cdrom',
            'debian-release': 'precise',
            'linux_template': 'true'
        },
        'recommendations': '',
        'PV_args': NO_VALUE,
        'suspend_SR': NO_VALUE,
    }


class ExpectedXenServerVIF(ExpectedXenServerObject):
    """
    A matcher for a XenServer VIF object.
    """
    default_fields = {
        'device': '0',
        'network': NO_VALUE,
        'VM': NO_VALUE,
        'MAC': '',
        'MTU': '1500',
        'qos_algorithm_type': '',
        'qos_algorithm_params': {},
        'other_config': {}
    }
