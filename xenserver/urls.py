from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.contrib import admin

urlpatterns = patterns(
    '',
    # Index
    url(r'^$', 'xenserver.views.index', name='home'),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico')),  # noqa: E501

    # Groups
    url(r'^group/create$', 'xenserver.views.group_create', name='group_create'),   # noqa: E501
    url(r'^group/move/(?P<vm>[\w-]+)/(?P<group>[\w-]+)$', 'xenserver.views.group_move', name='group_move'),  # noqa: E501
    url(r'^group/edit/(?P<id>[\w-]+)$', 'xenserver.views.group_edit', name='group_edit'),  # noqa: E501

    # Zones
    url(r'^zones/$', 'xenserver.views.zone_index', name='zone_index'),
    url(r'^zones/create$', 'xenserver.views.zone_create', name='zone_create'),
    url(r'^zones/edit/(?P<id>[\w-]+)$', 'xenserver.views.zone_edit', name='zone_edit'),  # noqa: E501
    url(r'^zones/view/(?P<id>[\w-]+)$', 'xenserver.views.zone_view', name='zone_view'),  # noqa: E501

    url(r'^zones/create_pool/(?P<zone>[\w-]+)$', 'xenserver.views.pool_create', name='pool_create'),  # noqa: E501
    url(r'^zones/edit_pool/(?P<id>[\w-]+)$', 'xenserver.views.pool_edit', name='pool_edit'),  # noqa: E501
    url(r'^zones/delete_pool/(?P<id>[\w-]+)$', 'xenserver.views.pool_delete', name='pool_delete'),  # noqa: E501

    # Servers
    url(r'^servers/$', 'xenserver.views.server_index', name='server_index'),
    url(r'^servers/create$', 'xenserver.views.server_create', name='server_create'),  # noqa: E501
    url(r'^servers/edit/(?P<id>[\w-]+)$', 'xenserver.views.server_edit', name='server_edit'),  # noqa: E501
    url(r'^servers/view/(?P<id>[\w-]+)$', 'xenserver.views.server_view', name='server_view'),  # noqa: E501

    # VMs
    url(r'^vm/view/(?P<id>[\w-]+)$', 'xenserver.views.vm_view', name='vm_view'),  # noqa: E501

    # Templates
    url(r'^templates/$', 'xenserver.views.template_index', name='template_index'),  # noqa: E501
    url(r'^templates/create$', 'xenserver.views.template_create', name='template_create'),  # noqa: E501
    url(r'^templates/edit/(?P<id>[\w-]+)$', 'xenserver.views.template_edit', name='template_edit'),  # noqa: E501

    url(r'^preseed/(?P<id>[\w-]+)$', 'xenserver.views.get_preseed', name='get_preseed'),  # noqa: E501


    # API stuff
    url(r'^start_vm/(?P<id>[\w-]+)$', 'xenserver.views.start_vm', name='start_vm'),  # noqa: E501
    url(r'^reboot_vm/(?P<id>[\w-]+)$', 'xenserver.views.reboot_vm', name='reboot_vm'),  # noqa: E501
    url(r'^stop_vm/(?P<id>[\w-]+)$', 'xenserver.views.stop_vm', name='stop_vm'),  # noqa: E501
    url(r'^terminate_vm/(?P<id>[\w-]+)$', 'xenserver.views.terminate_vm', name='terminate_vm'),  # noqa: E501
    url(r'^provision/$', 'xenserver.views.provision', name='provision'),

    url(r'^metrics/(?P<id>[\w-]+)$', 'xenserver.views.get_metrics', name='get_metrics'),  # noqa: E501

    url(r'^provision/completed/(?P<hostname>.+)$', 'xenserver.views.complete_provision', name='complete_provision'),  # noqa: E501

    # Authentication
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),  # noqa: E501
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='auth_logout'),  # noqa: E501
    url(r'^accounts/profile/$', 'xenserver.views.accounts_profile', name='accounts_profile'),  # noqa: E501
    url(r'^logs/$', 'xenserver.views.log_index', name='logs'),

    url(r'', include('social_auth.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
