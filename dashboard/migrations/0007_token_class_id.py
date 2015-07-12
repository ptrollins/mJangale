# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_user_class_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='token',
            name='class_id',
            field=models.CharField(default=b'*', max_length=5),
            preserve_default=True,
        ),
    ]
