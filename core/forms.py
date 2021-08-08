from django import forms
from django.core.validators import FileExtensionValidator

from .models import Plugin
from .utils import get_MD5

class PluginCreateForm(forms.ModelForm):
    ZIP_NAME = 'plugin_zip_file'
    ALLOWED_EXTENSIONS = ['zip']

    class Meta:
        model = Plugin
        fields = ['username', 'name', 'interval', 'should_run']

    plugin_zip_file = forms.fields.FileField(
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)])


    def clean_plugin_zip_file(self):
        data = self.cleaned_data[self.ZIP_NAME]

        try:
            hash = get_MD5(data)
            plugin: Plugin = Plugin.objects.get(hash_name=hash)
        except Plugin.DoesNotExist:
            plugin = None

        if plugin:
            raise forms.ValidationError(f'Plugin {data.name} already exists with name {plugin.name}')
        else:
            self.cleaned_data['hash_name'] = hash
            return data
