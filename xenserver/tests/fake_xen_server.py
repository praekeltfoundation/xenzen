from copy import deepcopy
from uuid import uuid4
import xmlrpclib

import xenapi


MEM_OVERHEAD = 1*1024*1024*1024


def mkref(name):
    return "Ref:%s:%s" % (name, uuid4())


class FakeXenServer(object):
    """
    Fake XenServer to use in tests.
    """

    hostname = "localhost"
    username = "user"
    password = "pass"

    def __init__(self, handlers=None, verbose=0):
        self.handlers = handlers or {}
        self.verbose = verbose
        self.sessions = {}
        self.SRs = {}
        self.VDIs = {}
        self.networks = {}
        self.PIFs = {}
        self.VMs = {}
        self.VIFs = {}
        self.VBDs = {}
        self.VM_operations = []
        self.hosts = {}
        self.pools = {}
        self.host_metrics = {}

    def getSession(self, hostname=hostname, username=username,
                   password=password):
        url = 'https://%s/' % (hostname)
        # First acquire a valid session by logging in:
        session = xenapi.Session(
            url, transport=StubTransport(self), verbose=self.verbose)
        session.xenapi.login_with_password(username, password)

        return session

    def handle_request(self, request):
        assert request.host == self.hostname
        args, method = xmlrpclib.loads(request.body)
        # print (args, method)
        result = self.call_method(method, args)
        result_dict = {'Status': 'Success', 'Value': result}
        # print response
        response_body = xmlrpclib.dumps((result_dict,), methodresponse=1)
        return Response(request, 200, response_body)

    def call_method(self, method, args):
        handler = self.handlers.get(method)
        if handler is None:
            handler = getattr(self, 'h_' + method.replace('.', '_'), None)
        if handler is None:
            raise RuntimeError("No such method: %s" % (method,))
        assert handler is not None
        return handler(*args)

    # State management helpers.

    def add_SR(self, name_label, type, **kw):
        kw['name_label'] = name_label
        kw['type'] = type
        kw.setdefault('VDIs', [])
        ref = mkref("SR")
        self.SRs[ref] = kw
        return ref

    def add_VDI(self, SR, name_label, **kw):
        kw['SR'] = SR
        kw['name_label'] = name_label
        ref = mkref("VDI")
        self.SRs[SR]['VDIs'].append(ref)
        self.VDIs[ref] = kw
        return ref

    def add_network(self, bridge, **kw):
        ref = mkref("network")
        kw['bridge'] = bridge
        kw.setdefault('PIFs', [])
        self.networks[ref] = kw
        return ref

    def add_PIF(self, network, device, gateway="", **kw):
        ref = mkref("PIF")
        kw['network'] = network
        kw['device'] = device
        kw['gateway'] = gateway
        self.networks[network]['PIFs'].append(ref)
        self.PIFs[ref] = kw
        return ref

    def list_network_VIFs_for_VM(self, VM):
        VIFs = []
        for ref, VIF in self.VIFs.items():
            if VIF["VM"] == VM:
                VIFs.append((VIF["network"], ref))
        return sorted(VIFs)

    def list_SR_VBDs_for_VM(self, VM):
        VDI_SRs = {ref: VDI["SR"] for ref, VDI in self.VDIs.items()}
        VBDs = []
        for ref, VBD in self.VBDs.items():
            if VBD["VM"] == VM:
                VBDs.append((VDI_SRs[VBD["VDI"]], ref))
        return sorted(VBDs)

    def add_host(self, API_version, mem, **kw):
        ref = mkref("host")
        metrics_ref = mkref("host_metrics")
        kw['metrics'] = metrics_ref
        kw['API_version_major'], kw['API_version_minor'] = API_version
        self.hosts[ref] = kw
        self.host_metrics[metrics_ref] = {
            "memory_total": mem,
            "memory_free": mem - MEM_OVERHEAD,
        }
        return ref

    def add_pool(self, master_host, **kw):
        ref = mkref("pool")
        kw['master'] = master_host
        self.pools[ref] = kw
        return ref

    # XMLRPC handler methods.

    def h_session_login_with_password(self, username, password):
        assert (username, password) == (self.username, self.password)
        ref = mkref("session")
        self.sessions[ref] = None
        return ref

    def h_SR_get_all(self, session):
        assert session in self.sessions
        return self.SRs.keys()

    def h_SR_get_record(self, session, ref):
        assert session in self.sessions
        return self.SRs[ref]

    def h_VDI_get_record(self, session, ref):
        assert session in self.sessions
        return self.VDIs[ref]

    def h_network_get_all(self, session):
        assert session in self.sessions
        return self.networks.keys()

    def h_network_get_record(self, session, ref):
        assert session in self.sessions
        return self.networks[ref]

    def h_PIF_get_all(self, session):
        assert session in self.sessions
        return self.PIFs.keys()

    def h_PIF_get_record(self, session, ref):
        assert session in self.sessions
        return self.PIFs[ref]

    def h_PIF_get_network(self, session, ref):
        assert session in self.sessions
        return self.PIFs[ref]["network"]

    def h_VM_create(self, session, params):
        assert session in self.sessions
        ref = mkref("VM")
        self.VMs[ref] = {
            'is_a_snapshot': False,
            'is_a_template': False,
            'is_control_domain': False,
            'power_state': 'Running',
            'uuid': str(uuid4()),
        }
        self.VMs[ref].update(deepcopy(params))
        return ref

    def h_VIF_create(self, session, params):
        assert session in self.sessions
        ref = mkref("VIF")
        VM = params["VM"]
        self.VMs[VM].setdefault("VIFs", []).append(ref)
        self.VIFs[ref] = deepcopy(params)
        return ref

    def h_VDI_create(self, session, params):
        assert session in self.sessions
        ref = mkref("VDI")
        self.VDIs[ref] = deepcopy(params)
        return ref

    def h_VBD_create(self, session, params):
        assert session in self.sessions
        ref = mkref("VBD")
        VM = params["VM"]
        self.VMs[VM].setdefault("VBDs", []).append(ref)
        self.VBDs[ref] = deepcopy(params)
        return ref

    def h_VM_start(self, session, ref, start_paused, force):
        assert session in self.sessions
        self.VM_operations.append((ref, "start"))
        return ""

    def h_session_logout(self, session):
        assert session in self.sessions
        self.sessions.pop(session)
        return ""

    def h_pool_get_all(self, session):
        assert session in self.sessions
        return self.pools.keys()

    def h_pool_get_master(self, session, pool):
        assert session in self.sessions
        return self.pools[pool]["master"]

    def h_host_get_API_version_major(self, session, host):
        assert session in self.sessions
        return self.hosts[host]["API_version_major"]

    def h_host_get_API_version_minor(self, session, host):
        assert session in self.sessions
        return self.hosts[host]["API_version_minor"]

    def h_host_get_all(self, session):
        assert session in self.sessions
        return self.hosts.keys()

    def h_host_get_record(self, session, host):
        # NOTE: This returns whatever we have in the host dict. It does not
        # validate or filter fields in any way.
        assert session in self.sessions
        return self.hosts[host]

    def h_host_get_metrics(self, session, host):
        assert session in self.sessions
        return self.hosts[host]['metrics']

    def h_host_metrics_get_record(self, session, metrics):
        # NOTE: This returns a partial metrics dict containing only the fields
        # we directly use.
        assert session in self.sessions
        md = self.host_metrics[metrics]
        # TODO: Subtract VM memory usage.
        return {
            "memory_total": str(md["memory_total"]),
            "memory_free": str(md["memory_free"]),
        }

    def h_VM_get_all_records(self, session):
        assert session in self.sessions
        return self.VMs

    def h_VM_get_record(self, session, vm):
        assert session in self.sessions
        return self.VMs[vm]


class Request(object):
    """
    Fake request object.
    """

    def __init__(self, host, handler, body):
        self.host = host
        self.handler = handler
        self.body = body

    def __repr__(self):
        return "<Request host=%r handler=%r body=%r>" % (
            self.host, self.handler, self.body)


class Response(object):
    """
    Fake response object.
    """

    def __init__(self, request, code, body):
        self.request = request
        self.code = code
        self.body = body

    def __repr__(self):
        return "<Response code=%r body=%r>" % (self.code, self.body)


class StubTransport(xmlrpclib.Transport):
    def __init__(self, xenserver):
        xmlrpclib.Transport.__init__(self)
        self.xenserver = xenserver

    def request(self, host, handler, request_body, verbose=0):
        """
        Fake a request.
        """
        request = Request(host, handler, request_body)
        if verbose:
            print request
        response = self.xenserver.handle_request(request)
        if verbose:
            print response
        return self.parse_response(response)

    def parse_response(self, response):
        """
        Feed the response to the parser.
        """
        p, u = self.getparser()
        p.feed(response.body)
        p.close()
        return u.close()
