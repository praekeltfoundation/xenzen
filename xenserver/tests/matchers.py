"""
Some helpers for testing XenServer stuff.
"""

from copy import deepcopy


class BaseMatcher(object):
    """
    The base class for a matcher that does fancy equality checks.
    """
    def match(self, other):
        raise NotImplementedError()

    def __eq__(self, other):
        return self.match(other)

    def __ne__(self, other):
        return not self.match(other)


class GenericMatcher(BaseMatcher):
    """
    A matcher that accepts an arbitrary match function.
    """
    def __init__(self, match, repr_str):
        self._match_func = match
        self._repr_str = repr_str

    def match(self, other):
        return self._match_func(other)

    def __repr__(self):
        return self._repr_str


NO_VALUE = GenericMatcher(lambda _: False, "<NO VALUE>")
ANY_VALUE = GenericMatcher(lambda _: True, "<ANY VALUE>")


class MatchSorted(BaseMatcher):
    def __init__(self, expected):
        self._expected = sorted(expected)

    def match(self, other):
        return self._expected == sorted(other)

    def __repr__(self):
        return "<SORTED %r>" % (self._expected,)


class ExtractValue(BaseMatcher):
    """
    A matcher that will extract whatever value it's compared to.
    """
    def __init__(self, name):
        self.name = name
        self.value = NO_VALUE

    def __repr__(self):
        return "<ExtractValue %s=%r>" % (self.name, self.value)

    def __cmp__(self, other):
        return cmp(self.value, other)

    def match(self, other):
        if self.value is not NO_VALUE:
            return self.value == other
        self.value = other
        return True


class ExtractValues(object):
    """
    A container for working with multiple extracted values more easily.
    """
    def __init__(self, *names):
        for name in names:
            setattr(self, name, ExtractValue(name))

    def values(self, *names):
        return [getattr(self, name).value for name in names]


class ExpectedXenServerObject(BaseMatcher):
    """
    A base matcher for XenServer objects.
    """
    default_fields = None

    def __init__(self, **fields):
        self.fields = fields
        self.expected_fields = deepcopy(self.default_fields)
        self.expected_fields.update(self.fields)

    def match(self, other):
        return self.expected_fields == other

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
        'device': NO_VALUE,
        'network': NO_VALUE,
        'VM': NO_VALUE,
        'MAC': '',
        'MTU': '1500',
        'qos_algorithm_type': '',
        'qos_algorithm_params': {},
        'other_config': {}
    }
