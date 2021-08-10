import subprocess
import os

from django.db.models.query import QuerySet
from django.http.response import HttpResponse
from django.views.generic import ListView, DetailView, CreateView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView, UpdateView

from .models import Plugin
from .forms import PluginCreateForm
from .utils import extract_zip

app_name = 'core'


class PluginIndexView(ListView):
    model = Plugin
    template_name = f'{app_name}/index.html'
    context_object_name = 'plugins'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(PluginIndexView, self).get_context_data(**kwargs)
        plugins = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(plugins, self.paginate_by)

        try:
            plugins = paginator.page
        except PageNotAnInteger:
            plugins = paginator.page(1)
        except EmptyPage:
            plugins = paginator.page(paginator.num_pages)

        context['plugins'] = plugins
        return context


class PluginDetailView(DetailView):
    model = Plugin
    template_name = f'{app_name}/plugin_detail.html'
    context_object_name = 'plugin'


class PluginCreateView(CreateView):
    model = Plugin
    template_name_suffix = '_create_form'
    form_class = PluginCreateForm
    success_url = reverse_lazy('core:index')

    def form_valid(self, form: PluginCreateForm) -> HttpResponse:
        ZIP_NAME = 'plugin_zip_file'

        plugin = form.save(commit=False)
        plugin.hash_name = form.cleaned_data['hash_name']
        
        # Create venv
        # TODO: need to add functionality for specifying different python versions
        plugin.plugin_dest = 'core' + os.sep + 'plugin' + os.sep + form.cleaned_data['hash_name']
        venv_dest = plugin.plugin_dest + os.sep + '.venv'
        subprocess.run(['python', '-m', 'virtualenv', venv_dest, '-p', 'python'])

        # Install requirements
        python = venv_dest + os.sep + 'bin' + os.sep + 'python'
        requirements = plugin.plugin_dest + os.sep + 'requirements.txt'
        subprocess.run([python, '-m', 'pip', 'install', '-r', requirements])

        plugin.save()
        return super().form_valid(form)


class PluginUpdateView(UpdateView):
    model = Plugin
    template_name_suffix = '_update_form'
    context_object_name = 'plugin'
    fields = ('username', 'name', 'interval', 'should_run', )

    def get_success_url(self):
        return reverse_lazy('core:plugin_detail', kwargs={'pk': self.object.id})


class PluginDeleteView(DeleteView):
    model = Plugin
    template_name = f'{app_name}/plugin_delete.html'
    success_url = reverse_lazy('core:index')