from django.contrib import admin

from xenserver.models import XenServer, XenVM, Template

admin.site.register(XenServer)
admin.site.register(XenVM)
admin.site.register(Template)

