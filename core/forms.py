import os
from django import forms
from django.core.validators import FileExtensionValidator

from .models import Plugin
from .utils import extract_zip, md5_dir

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
            # extract zip to `core/plugin/tmp/`
            extract_zip(data, 'core/plugin/tmp/')
            # calculate hash on `core/plugin/tmp/`
            hash = md5_dir('core/plugin/tmp/')

            plugin: Plugin = Plugin.objects.get(hash_name=hash)
        except Plugin.DoesNotExist:
            plugin = None

        if plugin:
            raise forms.ValidationError(f'Plugin {plugin.name} already exists #{plugin.id}')
        else:
            # rename `core/plugin/tmp/` to `core/plugin/hash/`
            os.rename('core/plugin/tmp/', 'core/plugin/' + hash)
            self.cleaned_data['hash_name'] = hash
            return data
