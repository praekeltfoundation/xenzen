# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Addresses',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.CharField(max_length=128)),
                ('ip_int', models.BigIntegerField(db_index=True)),
                ('version', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AddressPool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subnet', models.CharField(unique=True, max_length=128)),
                ('gateway', models.CharField(max_length=128)),
                ('version', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('severity', models.IntegerField()),
                ('message', models.TextField()),
                ('username', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('max_cores', models.IntegerField(default=8)),
                ('max_memory', models.IntegerField(default=16384)),
                ('administrators', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('cores', models.IntegerField()),
                ('memory', models.IntegerField()),
                ('iso', models.CharField(max_length=255)),
                ('diskspace', models.IntegerField()),
                ('preseed', models.TextField(blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='XenMetrics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=128)),
                ('timeblob', models.TextField()),
                ('datablob', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='XenServer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hostname', models.CharField(unique=True, max_length=255)),
                ('username', models.CharField(max_length=255)),
                ('password', models.CharField(max_length=255)),
                ('memory', models.IntegerField(default=1)),
                ('mem_free', models.IntegerField(default=1)),
                ('cpu_util', models.IntegerField(default=1)),
                ('cores', models.IntegerField(default=1)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='XenVM',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('status', models.CharField(max_length=128)),
                ('xsref', models.CharField(unique=True, max_length=255)),
                ('uuid', models.CharField(max_length=255)),
                ('sockets', models.IntegerField()),
                ('memory', models.IntegerField()),
                ('ip', models.CharField(max_length=128, blank=True)),
                ('project', models.ForeignKey(to='xenserver.Project', null=True)),
                ('xenserver', models.ForeignKey(to='xenserver.XenServer', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='xenserver',
            name='zone',
            field=models.ForeignKey(to='xenserver.Zone'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='xenmetrics',
            name='vm',
            field=models.ForeignKey(to='xenserver.XenVM'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='addresspool',
            name='server',
            field=models.ForeignKey(blank=True, to='xenserver.XenServer', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='addresspool',
            name='zone',
            field=models.ForeignKey(to='xenserver.Zone'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='addresses',
            name='pool',
            field=models.ForeignKey(to='xenserver.AddressPool'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='addresses',
            name='vm',
            field=models.ForeignKey(blank=True, to='xenserver.XenVM', null=True),
            preserve_default=True,
        ),
    ]
