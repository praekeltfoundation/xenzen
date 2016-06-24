# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xenserver', '0004_auto_20160622_0825'),
    ]

    operations = [
        migrations.AlterField(
            model_name='template',
            name='bootopts',
            field=models.CharField(max_length=512, blank=True),
        ),
    ]
