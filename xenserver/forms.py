from django.contrib.auth.models import User
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
import models
import re


class BaseModelForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-8'
    helper.add_input(Submit('submit', 'Submit'))


class BaseForm(forms.Form):
    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-8'
    helper.add_input(Submit('submit', 'Submit'))


class XenServerForm(BaseModelForm):
    class Meta:
        model = models.XenServer
        exclude = (
            'cores', 'memory', 'mem_free', 'cpu_util'
        )


class UserForm(BaseModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), initial='')

    class Meta:
        model = User
        exclude = (
            'email', 'username', 'is_staff', 'is_active', 'is_superuser',
            'last_login', 'date_joined', 'groups', 'user_permissions'
        )


class ZoneForm(BaseModelForm):
    class Meta:
        model = models.Zone
        exclude = ()


class GroupForm(BaseModelForm):
    class Meta:
        exclude = ()
        model = models.Project


class PoolForm(BaseModelForm):

    class Meta:
        model = models.AddressPool
        exclude = ('zone', )


class ProvisionForm(BaseForm):
    hostname = forms.CharField()

    group = forms.ModelChoiceField(
        queryset=models.Project.objects.all().order_by('name'),
        required=True)

    zone = forms.ModelChoiceField(
        queryset=models.Zone.objects.all().order_by('name'),
        empty_label='Anywhere', required=False)

    server = forms.ModelChoiceField(
        queryset=models.XenServer.objects.all().order_by('hostname'),
        empty_label='Auto select', required=False)

    template = forms.ModelChoiceField(
        queryset=models.Template.objects.all().order_by('memory'))

    ipaddress = forms.CharField(
        required=False, help_text='Leave blank for automatic selection')

    extra_network_bridges = forms.CharField(required=False, help_text=(
        'Bridge device names for extra network devices (whitespace separated)'
        ' - for example, "xenbr1"'))

    def clean(self):
        cleaned_data = super(ProvisionForm, self).clean()

        ipre = re.compile("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])"
                          "\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|"
                          "25[0-5])(\/(\d|[1-2]\d|3[0-2]))$")

        if cleaned_data['ipaddress']:
            if not ipre.match(cleaned_data['ipaddress']):
                raise forms.ValidationError(
                    "Invalid IP address format - please specify CIDR format "
                    "w.x.y.z/c or leave blank")

        if cleaned_data['hostname']:
            hsclean = cleaned_data['hostname'].strip()
            if '.' not in hsclean:
                raise forms.ValidationError("Not a valid FQDN.")

            cleaned_data['hostname'] = hsclean

        extra_net = cleaned_data['extra_network_bridges'].split()
        cleaned_data['extra_network_bridges'] = extra_net

        return cleaned_data


class TemplateForm(BaseModelForm):
    cores = forms.IntegerField(
        initial=2,
        min_value=1, max_value=8,
        help_text="CPU cores (between 1 and 8)")

    memory = forms.IntegerField(
        initial=1024,
        min_value=1024, max_value=16385,
        help_text="Memory in MB (between 1024 and 16384)")

    diskspace = forms.IntegerField(
        initial=50,
        min_value=10,
        max_value=500,
        help_text="Disk space in GB (10..500)"
    )

    class Meta:
        model = models.Template
        exclude = ()
