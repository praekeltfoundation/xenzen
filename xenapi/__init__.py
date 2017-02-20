from __future__ import absolute_import

# XenAPI.py and provision.py are taken from:
# https://github.com/xapi-project/xen-api/tree/v1.25.0/scripts/examples/python

# We only seem to use the Session class
from .XenAPI import Session

__all__ = ['Session']
