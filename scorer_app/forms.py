from django import forms
from .models import Repository


class AddRepoForm(forms.ModelForm):
    class Meta:
        model = Repository
        fields = ['full_name', 'url']
        labels = {
            'full_name': 'Название (owner/repo)',
            'url': 'Ссылка на GitHub',
        }
        help_texts = {
            'full_name': 'Например: django/django',
            'url': 'https://github.com/owner/repo',
        }