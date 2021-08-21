from typing import Any
import zipfile
from django.forms.models import BaseModelForm
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from core.utils import build_zip_json, extract_zip
import subprocess
import os
import shutil
import datetime

from django.views.generic import ListView, DetailView, CreateView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView, UpdateView
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.timezone import make_aware

from .models import Plugin
from .forms import PluginFormSet, PluginSourceForm

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
    form_class = PluginSourceForm
    template_name = 'core/plugin_create_form.html'
    success_url = reverse_lazy('core:index')

    def get_context_data(self, **kwargs):
        context = super(PluginCreateView, self).get_context_data(**kwargs)
        context['plugin_formset'] = PluginFormSet()
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        plugin_formset = PluginFormSet(self.request.POST)
        if form.is_valid() and plugin_formset.is_valid():
            return self.form_valid(form, plugin_formset)
        else:
            return self.form_invalid(form, plugin_formset)

    def form_valid(self, form: BaseModelForm, plugin_formset: PluginFormSet):
        # save PluginSource
        self.object = form.save(commit=False)
        self.object.source_dest = form.cleaned_data['source_dest']
        self.object.source_hash = form.cleaned_data['source_hash']
        # TODO: https://github.com/ICFL-UP/Yrden/issues/21
        self.object.source_file_hash = build_zip_json(
            zipfile.ZipFile(form.cleaned_data['plugin_zip_file']))
        self.object.upload_time = make_aware(datetime.datetime.now())
        self.object.upload_user = form.cleaned_data['upload_user']
        self.object.save()

        write_lines = [
            f'{self.object.source_hash}_{datetime.datetime.timestamp(self.object.upload_time)}\n',
            f'source_dest={self.object.source_dest}\n',
            f'upload_time={self.object.upload_time}\n',
            f'upload_user={self.object.upload_user}\n',
            f'source_file_hash={self.object.source_file_hash}'
        ]
        file_path = self.object.source_dest + os.sep + 'create_log_' + \
            str(datetime.datetime.timestamp(self.object.upload_time)) + '.txt'
        with open(file_path, 'x') as file:
            file.writelines(write_lines)

        # save Plugin
        plugin = plugin_formset.save(commit=False)
        plugin[0].plugin_source = self.object
        plugin[0].plugin_dest = 'core' + os.sep + \
            'plugin' + os.sep + self.object.source_hash
        extract_zip(
            form.cleaned_data['plugin_zip_file'], plugin[0].plugin_dest)
        plugin[0].save()

        # # Create venv
        # # TODO: https://github.com/ICFL-UP/Yrden/issues/26
        # venv_dest = plugin[0].plugin_dest + os.sep + '.venv'
        # subprocess.run(['python', '-m', 'virtualenv',
        #                venv_dest, '-p', 'python'])
        # python = venv_dest + os.sep + 'bin' + os.sep + 'python'
        # requirements = plugin[0].plugin_dest + os.sep + 'requirements.txt'
        # subprocess.run([python, '-m', 'pip', 'install', '-r', requirements])

        return redirect(reverse("core:index"))

    def form_invalid(self, form, plugin_formset):
        return self.render_to_response(
            self.get_context_data(form=form,
                                  product_meta_formset=plugin_formset
                                  )
        )


class PluginDeleteView(DeleteView):
    model = Plugin
    template_name = f'{app_name}/plugin_delete.html'
    success_url = reverse_lazy('core:index')

    def delete(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        object: Plugin = self.get_object()
        user = self.request.POST.get('username')
        source_dest = object.plugin_source.source_dest

        shutil.rmtree(object.plugin_dest)

        deleted_time = datetime.datetime.now()

        write_lines = [
            f'{object.plugin_source.source_hash}_{datetime.datetime.timestamp(deleted_time)}\n',
            f'delete_user={user}\n',
            f'deleted_time={deleted_time}\n',
        ]
        file_path = object.plugin_source.source_dest + os.sep + 'delete_log_' + \
            str(datetime.datetime.timestamp(deleted_time)) + '.txt'
        with open(file_path, 'x') as file:
            file.writelines(write_lines)

        shutil.move(source_dest, 'core' + os.sep + 'source' +
                    os.sep + 'deleted_' + object.plugin_source.source_hash)

        return super().delete(request, *args, **kwargs)
