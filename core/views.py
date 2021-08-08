import subprocess
import os

from django.db.models.query import QuerySet
from django.http.response import HttpResponse
from django.views import generic

from .models import Plugin
from .forms import PluginCreateForm
from .utils import extract_zip

app_name = 'core'


class PluginIndexView(generic.ListView):
    template_name = f'{app_name}/index.html'
    context_object_name = 'plugin_list'

    def get_queryset(self) -> QuerySet[Plugin]:
        """
        Return list of plugins for the system
        """
        return Plugin.objects.all()


class PluginDetailView(generic.DetailView):
    model = Plugin
    template_name = f'{app_name}/plugin_detail.html'


class PluginCreateView(generic.CreateView):
    template_name_suffix = '_create_form'
    model = Plugin
    form_class = PluginCreateForm

    def form_valid(self, form: PluginCreateForm) -> HttpResponse:
        ZIP_NAME = 'plugin_zip_file'

        plugin = form.save(commit=False)
        plugin.hash_name = form.cleaned_data['hash_name']

        file = form.cleaned_data[ZIP_NAME]
        plugin_dir = 'core' + os.sep + 'plugin' + os.sep + form.cleaned_data['hash_name']
        plugin.plugin_dest = plugin_dir
        extract_zip(file, plugin_dir)
        
        # Create venv
        # TODO: need to add functionality for specifying different python versions
        venv_dest = plugin_dir + os.sep + '.venv'
        form.cleaned_data['venv_dest'] = venv_dest
        subprocess.run(['python', '-m', 'virtualenv', venv_dest, '-p', 'python'])

        # Install requirements
        python = venv_dest + os.sep + 'bin' + os.sep + 'python'
        requirements = plugin_dir + os.sep + 'requirements.txt'
        subprocess.run([python, '-m', 'pip', 'install', '-r', requirements])

        plugin.save()
        return super().form_valid(form)