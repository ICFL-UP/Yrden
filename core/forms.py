import os
from io import BufferedReader
from django import forms
from django.core.validators import FileExtensionValidator
from django.forms.models import inlineformset_factory

from .models import Plugin, PluginSource
from .utils import get_MD5, store_zip_file


class PluginSourceForm(forms.ModelForm):
    ZIP_NAME = 'plugin_zip_file'
    ALLOWED_EXTENSIONS = ['zip']

    class Meta:
        model = PluginSource
        fields = ['upload_user']

    plugin_zip_file = forms.fields.FileField(
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)])

    def clean_plugin_zip_file(self):
        data: BufferedReader = self.cleaned_data[self.ZIP_NAME]

        try:
            # get hash of zip
            zip_hash: str = get_MD5(data)

            # validate plugin uniqueness
            pluginSource: PluginSource = PluginSource.objects.get(source_hash = zip_hash)

        except PluginSource.DoesNotExist:
            pluginSource = None

        if pluginSource:
            raise forms.ValidationError(f'Plugin {pluginSource.source_hash} already exists #{pluginSource.id}')
        else:
            # if plugin does not exist

            # store plugin source
            self.cleaned_data['source_hash'] = zip_hash
            self.cleaned_data['source_dest'] = 'core' + os.sep + 'source' + os.sep + zip_hash
            store_zip_file(data, self.cleaned_data['source_dest'])

            # build JSON of source files
            # file: hash

            return data


class PluginForm(forms.ModelForm):
    class Meta:
        model = Plugin
        fields = ['name', 'interval', 'should_run']
        exclude = ('plugin_source', )

PluginFormSet = inlineformset_factory(PluginSource, Plugin, form=PluginForm, can_delete=False)
