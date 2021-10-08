import os

from io import BufferedReader
from datetime import datetime
from django import forms
from django.core.validators import FileExtensionValidator
from django.forms import fields
from django.forms.models import inlineformset_factory
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Plugin, PluginSource
from .utils import get_MD5, get_python_choices, store_zip_file


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user: User = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class PluginSourceForm(forms.ModelForm):
    ZIP_NAME = 'plugin_zip_file'
    ALLOWED_EXTENSIONS = ['zip']

    class Meta:
        model = PluginSource
        exclude = ('source_dest', 'source_hash', 'upload_time',
                   'upload_user', 'source_file_hash', 'deleted_at')

    plugin_zip_file = forms.fields.FileField(
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)])

    def clean_plugin_zip_file(self):
        data: BufferedReader = self.cleaned_data[self.ZIP_NAME]

        try:
            upload_time = timezone.now()
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
                str(datetime.timestamp(upload_time))
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
        fields = ['plugin_name', 'interval', 'should_run']

    version = forms.fields.ChoiceField(choices=get_python_choices())

    def clean_version(self):
        data: int = int(self.cleaned_data['version'])
        python_version: str = self.declared_fields['version'].choices[data][1]

        self.cleaned_data['python_version'] = python_version
        return data


PluginFormSet = inlineformset_factory(
    PluginSource, Plugin, form=PluginForm, can_delete=False)
