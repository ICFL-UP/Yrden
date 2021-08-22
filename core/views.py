import json
from typing import Any
import zipfile
from django.db.models.query import QuerySet
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
        self.object.upload_time = form.cleaned_data['upload_time']
        self.object.upload_user = form.cleaned_data['upload_user']
        self.object.save()

        log_json: dict = {
            'log_datetime': datetime.datetime.timestamp(datetime.datetime.now()),
            'source_dest': self.object.source_dest,
            'source_hash': self.object.source_hash,
            'upload_time': self.object.upload_time.strftime("%m/%d/%Y, %H:%M:%S"),
            'upload_user': self.object.upload_user,
            'source_file_hash': json.loads(self.object.source_file_hash)
        }
        file_path = self.object.source_dest + os.sep + 'create' + \
            str(datetime.datetime.timestamp(self.object.upload_time)) + '.json'
        with open(file_path, 'x') as file:
            file.write(json.dumps(log_json))

        # save Plugin
        plugin = plugin_formset.save(commit=False)
        plugin[0].plugin_source = self.object
        plugin[0].plugin_dest = 'core' + os.sep + \
            'plugin' + os.sep + self.object.source_hash + '_' +  \
            str(datetime.datetime.timestamp(self.object.upload_time))
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
        deleted_dest = 'core' + os.sep + 'source' + os.sep + 'deleted_' + object.plugin_source.source_hash + \
            '_' + str(datetime.datetime.timestamp(object.plugin_source.upload_time))

        log_json: dict = {
            'log_datetime': datetime.datetime.timestamp(deleted_time),
            'source_dest': object.plugin_source.source_dest,
            'source_hash': object.plugin_source.source_hash,
            'upload_time': object.plugin_source.upload_time.strftime("%m/%d/%Y, %H:%M:%S"),
            'upload_user': object.plugin_source.upload_user,
            'source_file_hash': json.loads(object.plugin_source.source_file_hash),
            'username': user,
            'deleted_dest': deleted_dest
        }
        file_path = object.plugin_source.source_dest + os.sep + 'delete' + \
            str(datetime.datetime.timestamp(deleted_time)) + '.json'
        with open(file_path, 'x') as file:
            file.write(json.dumps(log_json))

        shutil.move(source_dest, deleted_dest)

        object.plugin_source.source_hash = 'deleted_' + object.plugin_source.source_hash
        object.plugin_source.source_dest = deleted_dest
        object.plugin_source.save()

        return super().delete(request, *args, **kwargs)
