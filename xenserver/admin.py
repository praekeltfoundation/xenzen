from django.contrib import admin

from xenserver.models import (
    Addresses, AddressPool, Template, XenServer, XenVM)

admin.site.register(XenServer)
admin.site.register(XenVM)
admin.site.register(Template)
admin.site.register(Addresses)
admin.site.register(AddressPool)
