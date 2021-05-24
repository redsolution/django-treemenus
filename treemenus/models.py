import os
import re
import json
from itertools import chain
from unidecode import unidecode
from django.template.defaultfilters import slugify
from django.utils.encoding import smart_text
from django.utils.deconstruct import deconstructible
from django.core.cache import cache
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from django.forms.models import model_to_dict
from .settings import NAMES


@deconstructible
class SlugifyUpload(object):

    """ Class for converting file name to Latin before saving"""

    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        filename, ext = filename.rsplit('.', 1)
        filename = re.sub(r'[_.,:;@#$%^&?*|()\[\]]', '-', filename)
        filename = slugify(unidecode(smart_text(filename)))
        full_filename = '.'.join([filename, ext])
        return os.path.join(self.sub_path, full_filename)


class MenuItem(models.Model):

    class Meta:
        verbose_name = _('menu item')
        verbose_name_plural = _('menu items')


    parent = models.ForeignKey('self', verbose_name=_('parent'), null=True, blank=True, on_delete=models.CASCADE)
    show = models.BooleanField(verbose_name=_('show'), default=True)
    caption = models.CharField(_('caption'), max_length=255)
    add_caption = models.CharField(_('add caption'), null=True, blank=True, max_length=255)
    url = models.CharField(_('url'), max_length=200, blank=True)
    image = models.FileField(verbose_name=_('image'), blank=True, null=True, upload_to=SlugifyUpload('upload/menu'))
    level = models.IntegerField(_('level'), default=0, editable=False)
    rank = models.IntegerField(_('rank'), default=0, editable=False)
    menu = models.ForeignKey('Menu', related_name='contained_items', verbose_name=_('menu'), null=True, blank=True, editable=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.caption

    def save(self, force_insert=False, **kwargs):
        from treemenus.utils import clean_ranks

        # Calculate level
        old_level = self.level
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 0

        if self.pk:
            new_parent = self.parent
            old_parent = MenuItem.objects.get(pk=self.pk).parent
            if old_parent != new_parent:
                #If so, we need to recalculate the new ranks for the item and its siblings (both old and new ones).
                if new_parent:
                    clean_ranks(new_parent.children())  # Clean ranks for new siblings
                    self.rank = new_parent.children().count()
                super(MenuItem, self).save(force_insert, **kwargs)  # Save menu item in DB. It has now officially changed parent.
                if old_parent:
                    clean_ranks(old_parent.children())  # Clean ranks for old siblings
            else:
                super(MenuItem, self).save(force_insert, **kwargs)  # Save menu item in DB

        else:  # Saving the menu item for the first time (i.e creating the object)
            if not self.has_siblings():
                # No siblings - initial rank is 0.
                self.rank = 0
            else:
                # Has siblings - initial rank is highest sibling rank plus 1.
                siblings = self.siblings().order_by('-rank')
                self.rank = siblings[0].rank + 1
            super(MenuItem, self).save(force_insert, **kwargs)

        # If level has changed, force children to refresh their own level
        if old_level != self.level:
            for child in self.children():
                child.save()  # Just saving is enough, it'll refresh its level correctly.

    def delete(self, using=None):
        from treemenus.utils import clean_ranks
        old_parent = self.parent
        super(MenuItem, self).delete()
        if old_parent:
            clean_ranks(old_parent.children())

    def caption_with_spacer(self):
        spacer = ''
        for i in range(0, self.level):
            spacer += '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
        if self.level > 0:
            spacer += '|-&nbsp;'
        return '%s%s' % (spacer, self.caption)

    def get_flattened(self):
        flat_structure = [self]
        for child in self.children():
            flat_structure = chain(flat_structure, child.get_flattened())
        return flat_structure

    def siblings(self):
        if not self.parent:
            return MenuItem.objects.none()
        else:
            if not self.pk:  # If menu item not yet been saved in DB (i.e does not have a pk yet)
                return self.parent.children()
            else:
                return self.parent.children().exclude(pk=self.pk)

    def has_siblings(self):
        return self.siblings().count() > 0

    def children(self):
        _children = MenuItem.objects.filter(parent=self).order_by('rank',)
        for child in _children:
            child.parent = self  # Hack to avoid unnecessary DB queries further down the track.
        return _children

    def has_children(self):
        return self.children().count() > 0

    def get_data(self):
        data = model_to_dict(self, exclude=['parent', 'menu', 'image'])
        data['image'] = self.image.url if self.image else ''
        data['children'] = []
        for item in self.children():
            data['children'].append(item.get_data())
        data['has_children'] = bool(data['children'])
        return data

    def delete_cache_data(self):
        if hasattr(self, 'menu'):
            self.menu.delete_cache_data()


class MenuManager(models.Manager):
    pass


class Menu(models.Model):
    name = models.CharField(_('name'), max_length=50, unique=True)
    show = models.BooleanField(verbose_name=_('show'), default=True)
    root_item = models.ForeignKey(MenuItem, related_name='is_root_item_of', verbose_name=_('root item'), null=True, blank=True, editable=False, on_delete=models.CASCADE)

    objects = MenuManager()

    def save(self, force_insert=False, **kwargs):
        if not self.root_item:
            root_item = MenuItem()
            root_item.caption = NAMES.get(self.name)
            if not self.pk:  # If creating a new object (i.e does not have a pk yet)
                super(Menu, self).save(force_insert, **kwargs)  # Save, so that it gets a pk
                force_insert = False
            root_item.menu = self
            root_item.save()  # Save, so that it gets a pk
            self.root_item = root_item
        super(Menu, self).save(force_insert, **kwargs)

    def delete(self, using=None):
        if self.root_item is not None:
            self.root_item.delete()
        super(Menu, self).delete()

    @property
    def show(self):
        return bool(self.contained_items.filter(level=1, show=True))

    def get_data(self):
        data = model_to_dict(self, exclude=['root_item'])
        data['root_item'] = self.root_item.get_data()
        return data

    def get_cache_data(self):
        json_data = cache.get(self.name)
        if json_data:
            return json.loads(json_data)
        else:
            data = self.get_data()
            cache.set(self.name, json.dumps(data, ensure_ascii=False))
            return data

    def delete_cache_data(self):
        cache.delete(self.name)

    def __str__(self):
        return NAMES.get(self.name)

    class Meta:
        verbose_name = _('Menu')
        verbose_name_plural = _('Menus')
