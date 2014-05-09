from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Index
    url(r'^$', 'xenserver.views.index', name='home'),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico')),

    # Groups
    url(r'^group/create$', 'xenserver.views.group_create', name='group_create'),
    url(r'^group/move/(?P<vm>[\w-]+)/(?P<group>[\w-]+)$', 'xenserver.views.group_move', name='group_move'),
    url(r'^group/edit/(?P<id>[\w-]+)$', 'xenserver.views.group_edit', name='group_edit'),

    # Zones
    url(r'^zones/$', 'xenserver.views.zone_index', name='zone_index'),
    url(r'^zones/create$', 'xenserver.views.zone_create', name='zone_create'),
    url(r'^zones/edit/(?P<id>[\w-]+)$', 'xenserver.views.zone_edit', name='zone_edit'),
    url(r'^zones/view/(?P<id>[\w-]+)$', 'xenserver.views.zone_view', name='zone_view'),

    # Servers
    url(r'^servers/$', 'xenserver.views.server_index', name='server_index'),
    url(r'^servers/create$', 'xenserver.views.server_create', name='server_create'),
    url(r'^servers/edit/(?P<id>[\w-]+)$', 'xenserver.views.server_edit', name='server_edit'),
    url(r'^servers/view/(?P<id>[\w-]+)$', 'xenserver.views.server_view', name='server_view'),

    # Templates
    url(r'^templates/$', 'xenserver.views.template_index', name='template_index'),
    url(r'^templates/create$', 'xenserver.views.template_create', name='template_create'),
    url(r'^templates/edit/(?P<id>[\w-]+)$', 'xenserver.views.template_edit', name='template_edit'),

    url(r'^preseed/(?P<id>[\w-]+)$', 'xenserver.views.get_preseed', name='get_preseed'),


    # API stuff
    url(r'^start_vm/(?P<id>[\w-]+)$', 'xenserver.views.start_vm', name='start_vm'),
    url(r'^reboot_vm/(?P<id>[\w-]+)$', 'xenserver.views.reboot_vm', name='reboot_vm'),
    url(r'^stop_vm/(?P<id>[\w-]+)$', 'xenserver.views.stop_vm', name='stop_vm'),
    url(r'^terminate_vm/(?P<id>[\w-]+)$', 'xenserver.views.terminate_vm', name='terminate_vm'),
    url(r'^provision/$', 'xenserver.views.provision', name='provision'),

    # Authentication
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='auth_logout'),
    url(r'^accounts/profile/$', 'xenserver.views.accounts_profile', name='accounts_profile'),
    url(r'^logs/$', 'xenserver.views.log_index', name='logs'),

    url(r'', include('social_auth.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
