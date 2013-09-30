from django.contrib.auth.models import User
from django import forms
from bootstrap.forms import BootstrapModelForm, BootstrapForm
import models


class XenServerForm(BootstrapModelForm):
    class Meta:
        model = models.XenServer
        exclude = (
            'cores', 'memory'
        )

class UserForm(BootstrapModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), initial='')
    class Meta:
        model = User
        exclude = (
            'email', 'username', 'is_staff', 'is_active', 'is_superuser',
            'last_login', 'date_joined', 'groups', 'user_permissions'
        )

class ProvisionForm(BootstrapForm):
    hostname = forms.CharField()
    memory = forms.IntegerField(
        initial=1024,
        min_value=1024, max_value=16385,
        help_text="Memory in MB (between 1024 and 16384)")

    cores = forms.IntegerField(
        initial=2,
        min_value=1, max_value=8,
        help_text="CPU cores (between 1 and 8)")

    diskspace = forms.IntegerField(
        initial=50, 
        min_value=10, 
        max_value=500, 
        help_text="Disk space in GB (10..500)"
    )
