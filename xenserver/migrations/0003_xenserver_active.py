# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xenserver', '0002_auto_20150109_0905'),
    ]

    operations = [
        migrations.AddField(
            model_name='xenserver',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
