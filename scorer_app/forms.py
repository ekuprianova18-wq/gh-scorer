from django import forms
from django.core.exceptions import ValidationError
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

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if Repository.objects.filter(full_name__iexact=full_name).exists():
            raise ValidationError('Репозиторий с таким названием уже существует.')
        return full_name