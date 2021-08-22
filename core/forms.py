import os
import datetime
from io import BufferedReader
from django import forms
from django.core.validators import FileExtensionValidator
from django.forms.models import inlineformset_factory
from django.utils.timezone import make_aware

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
            upload_time = make_aware(datetime.datetime.now())
            zip_hash: str = get_MD5(data)

            # validate plugin uniqueness
            pluginSource: PluginSource = PluginSource.objects.get(
                source_hash=zip_hash)
            plugin: Plugin = Plugin.objects.get(plugin_source=pluginSource)

        except PluginSource.DoesNotExist:
            pluginSource = None
        except Plugin.DoesNotExist:
            plugin = None

        if pluginSource and plugin:
            raise forms.ValidationError(
                f'Plugin exists for source: {pluginSource.source_hash} with id: {plugin.id}')
        elif (pluginSource and not plugin) or (not pluginSource):
            # if plugin does not exist

            # store plugin source
            self.cleaned_data['source_dest'] = 'core' + \
                os.sep + 'source' + os.sep + zip_hash + '_' + \
                str(datetime.datetime.timestamp(upload_time))
            self.cleaned_data['source_hash'] = zip_hash
            self.cleaned_data['upload_time'] = upload_time

            try:
                store_zip_file(data, self.cleaned_data['source_dest'])
            except FileExistsError:
                raise forms.ValidationError(
                    f'PluginSource files exists for location: {self.cleaned_data["source_data"]}')

            return data


class PluginForm(forms.ModelForm):
    class Meta:
        model = Plugin
        fields = ['name', 'interval', 'should_run']
        exclude = ('plugin_source', )


PluginFormSet = inlineformset_factory(
    PluginSource, Plugin, form=PluginForm, can_delete=False)
