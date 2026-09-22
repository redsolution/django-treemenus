# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('treemenus', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='menuitem',
            name='image',
            field=models.ImageField(help_text='PNG, JPG, GIF only.', upload_to='upload/menu', verbose_name='image', blank=True),
            preserve_default=True,
        ),
    ]
