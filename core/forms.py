import sys
import importlib.util

from django import forms
from django.core.validators import FileExtensionValidator
from zipfile import ZipFile

from .models import Plugin


class PluginCreateForm(forms.ModelForm):
    ZIP_NAME = 'plugin_zip_file'
    PACKAGE = 'core.plugin'
    PACKAGE_DIR = 'core/plugin'
    ALLOWED_EXTENSIONS = ['zip']

    class Meta:
        model = Plugin
        fields = ['name', 'interval', 'should_run']

    plugin_zip_file = forms.fields.FileField(
        validators=[FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)])

    def clean_name(self):
        data = self.cleaned_data['name']

        try:
            plugin = Plugin.objects.get(name=data)
        except Plugin.DoesNotExist:
            plugin = None

        if plugin:
            raise forms.ValidationError(
                "Plugin %s is already added. Make sure the name is unique." % data)

        return data

    def clean_plugin_zip_file(self):
        data = self.cleaned_data[self.ZIP_NAME]

        module_name = str(data.name).split('.')[0].lower()

        if module_name in sys.modules:
            raise forms.ValidationError(
                "Module %s already exists in sys.modules" % module_name)
        else:
            self.__extract_zip__(data)

        full_module_name = self.PACKAGE + '.' + module_name
        spec = importlib.util.find_spec(full_module_name)

        if spec is None:
            raise forms.ValidationError(
                "Cannot fine module %s" % full_module_name)
        else:
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

        return data

    def __extract_zip__(self, file):
        with ZipFile(file, 'r') as zipObj:
            zipObj.extractall(self.PACKAGE_DIR)
