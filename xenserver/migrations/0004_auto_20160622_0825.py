# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xenserver', '0003_xenserver_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='template',
            name='bootopts',
            field=models.CharField(max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='xenvm',
            name='template',
            field=models.ForeignKey(default=None, to='xenserver.Template', null=True),
        ),
    ]
