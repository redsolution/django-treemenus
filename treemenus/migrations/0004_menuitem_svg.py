# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('treemenus', '0003_auto_20180208_1301'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='svg',
            field=models.FileField(help_text='svg has higher priority over the image', upload_to='upload/menu', null=True, verbose_name='svg', blank=True),
            preserve_default=True,
        ),
    ]
