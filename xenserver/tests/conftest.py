import pytest


class TaskCatcher(object):
    def __init__(self, monkeypatch):
        self.mp = monkeypatch

    def patch_urlopen(self, f):
        """
        Replace urllib2.urlopen() with the given function.

        As far as I can tell, the only thing that calls urlopen() is
        tasks.getHostMetrics().
        """
        import urllib2
        self.mp.setattr(urllib2, 'urlopen', f)

    def catch_async(self, task, f=lambda *a: a):
        """
        Return a list that will be populated with the args of any call to the
        given task.
        """
        calls = []
        self.mp.setattr(task, 'apply_async', lambda *a: calls.append(f(*a)))
        return calls

    def catch_updateServer(self):
        """
        Special case of catch_async for updateServer.
        """
        from xenserver import tasks
        return self.catch_async(
            tasks.updateServer, lambda args, kwargs: args[0].hostname)

    def catch_updateVm(self):
        """
        Special case of catch_async for updateVm.
        """
        from xenserver import tasks
        return self.catch_async(
            tasks.updateVm,
            lambda args, kwargs: (args[0].hostname, args[1], args[2]))

    def catch_create_vm(self):
        """
        Special case of catch_async for create_vm.
        """
        from xenserver import tasks
        return self.catch_async(
            tasks.create_vm, lambda args, kwargs: args)


@pytest.fixture
def task_catcher(monkeypatch):
    """
    Monkey-patch the given task's apply_async() method to add calls to a
    list instead of queueing the task.
    """
    return TaskCatcher(monkeypatch)


@pytest.fixture
def xs_helper(monkeypatch):
    """
    Provide a XenServerHelper instance and monkey-patch xenserver.tasks to use
    sessions from that instance instead of making real API calls.
    """
    from xenserver import tasks
    from xenserver.tests.helpers import XenServerHelper
    xshelper = XenServerHelper()
    monkeypatch.setattr(tasks, 'getSession', xshelper.get_session)
    return xshelper
