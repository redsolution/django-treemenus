# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('treemenus', '0002_menuitem_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menuitem',
            name='image',
            field=models.ImageField(help_text='PNG, JPG, GIF only.', upload_to='upload/menu', null=True, verbose_name='image', blank=True),
            preserve_default=True,
        ),
    ]
