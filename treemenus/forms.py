from django import forms
from .models import Menu
from .settings import NAMES


class MenuAdminForm(forms.ModelForm):

    class Meta:
        model = Menu
        fields = '__all__'
        widgets = {
            'name': forms.Select(choices=[(key, name) for key, name in NAMES.items()])
        }

