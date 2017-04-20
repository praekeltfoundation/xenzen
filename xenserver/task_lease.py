"""
This module (ab)uses the database session store to provide task leases that
can be used to prevent a buildup of slow tasks.
"""

from __future__ import absolute_import

from datetime import timedelta

from celery.utils.log import get_task_logger
from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils import timezone

logger = get_task_logger(__name__)


def _key(task, args):
    return '::'.join(['lease', task, args])


def acquire(task, args, ttl=None):
    """
    Attempt to acquire a task lease for the given task. This should be done by
    the thing that queues the task for execution. Returns `True` is the lease
    has been acquired, `False` if an existing active lease is found.
    """
    key = _key(task, args)
    if Session.objects.filter(
            session_key=key, expire_date__gt=timezone.now()).exists():
        # There's an active lease, move on.
        logger.info("Active lease found for %s::%s." % (task, args))
        return False
    if ttl is None:
        ttl = settings.XENZEN_TASK_LEASE_SECONDS
    exp = timezone.now() + timedelta(ttl)
    lease = Session(session_key=key, session_data="", expire_date=exp)
    lease.save()
    return True


def release(task, args):
    """
    Release the task lease for given task, if it exists. This should be done by
    the task itself once it's finished.
    """
    key = _key(task, args)
    try:
        Session.objects.get(session_key=key).delete()
    except Session.DoesNotExist:
        pass
