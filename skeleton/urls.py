from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Index
    url(r'^$', 'xenserver.views.index', name='home'),

    # Servers
    url(r'^servers/$', 'xenserver.views.server_index', name='server_index'),
    url(r'^servers/create$', 'xenserver.views.server_create', name='server_create'),
    url(r'^servers/edit/(?P<id>[\w-]+)$', 'xenserver.views.server_edit', name='server_edit'),
    url(r'^servers/view/(?P<id>[\w-]+)$', 'xenserver.views.server_view', name='server_view'),

    url(r'^provision/$', 'xenserver.views.provision', name='provision'),

    # Authentication
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='auth_logout'),
    url(r'^accounts/profile/$', 'xenserver.views.accounts_profile', name='accounts_profile'),

    #url(r'', include('social_auth.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
