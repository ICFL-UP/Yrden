import logging
import os
import json
import shutil
import threading

from typing import Any, List
from django.forms.models import BaseModelForm
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.views.generic import ListView, DetailView, CreateView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin

from core.utils import build_zip_json, create_venv, extract_zip, write_log
from core.models import Plugin, PluginRun
from core.forms import PluginFormSet, PluginSourceForm
from core.enums.log_type_enum import LogType

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-9s) %(message)s',)


class PluginIndexView(LoginRequiredMixin, ListView):
    model = Plugin
    template_name = 'core/index.html'
    context_object_name = 'plugins'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(PluginIndexView, self).get_context_data(**kwargs)
        plugins = self.get_queryset()
        page = self.request.GET.get('page')
        paginator = Paginator(plugins, self.paginate_by)

        try:
            plugins = paginator.page(page)
        except PageNotAnInteger:
            plugins = paginator.page(1)
        except EmptyPage:
            plugins = paginator.page(paginator.num_pages)

        context['plugins'] = plugins
        return context


class PluginDetailView(LoginRequiredMixin, DetailView):
    model = Plugin
    template_name = 'core/plugin_detail.html'
    context_object_name = 'plugin'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(PluginDetailView, self).get_context_data(**kwargs)

        plugin_runs = PluginRun.objects.filter(plugin=self.kwargs['pk'])
        page = self.request.GET.get('page')
        paginator = Paginator(plugin_runs, self.paginate_by)

        try:
            plugin_runs = paginator.page(page)
        except PageNotAnInteger:
            plugin_runs = paginator.page(1)
        except EmptyPage:
            plugin_runs = paginator.page(paginator.num_pages)

        context['plugin_runs'] = plugin_runs
        return context


class PluginCreateView(LoginRequiredMixin, CreateView):
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
            return self.form_valid(form, plugin_formset, request.user)
        else:
            return self.form_invalid(form, plugin_formset)

    def form_valid(self, form: BaseModelForm, plugin_formset: PluginFormSet, user):
        # save PluginSource
        self.object = form.save(commit=False)
        self.object.source_dest = form.cleaned_data['source_dest']
        self.object.source_hash = form.cleaned_data['source_hash']
        self.object.upload_time = form.cleaned_data['upload_time']
        self.object.upload_user = user
        self.object.save()

        build_hash_thread = threading.Thread(
            target=build_zip_json, args=(form.cleaned_data['plugin_zip_file'].file, self.object))
        build_hash_thread.start()

        log_json: dict = {
            'log_datetime': datetime.timestamp(timezone.now()),
            'source_dest': self.object.source_dest,
            'source_hash': self.object.source_hash,
            'upload_time': self.object.upload_time.strftime("%m/%d/%Y, %H:%M:%S"),
            'upload_user_username': self.object.upload_user.username,
            'upload_user_email': self.object.upload_user.email,
        }
        write_log(LogType.CREATE, self.object, log_json)

        # save Plugin
        plugin: List[Plugin] = plugin_formset.save(commit=False)
        plugin[0].plugin_source = self.object
        plugin[0].plugin_dest = 'core' + os.sep + \
            'plugin' + os.sep + self.object.source_hash + '_' +  \
            str(datetime.timestamp(self.object.upload_time))
        extract_zip_thread = threading.Thread(target=extract_zip, args=(
            form.cleaned_data['plugin_zip_file'], plugin[0].plugin_dest))
        extract_zip_thread.start()

        plugin[0].save()

        extract_zip_thread.join()

        venv_thread = threading.Thread(target=create_venv, args=(plugin[0], ))
        venv_thread.start()

        return redirect(reverse("core:index"))

    def form_invalid(self, form, plugin_formset):
        return self.render_to_response(
            self.get_context_data(form=form,
                                  product_meta_formset=plugin_formset
                                  )
        )


class PluginDeleteView(LoginRequiredMixin, DeleteView):
    model = Plugin
    template_name = 'core/plugin_delete.html'
    success_url = reverse_lazy('core:index')

    def delete(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        object: Plugin = self.get_object()
        user = request.user
        source_dest = object.plugin_source.source_dest

        shutil.rmtree(object.plugin_dest)

        deleted_time = timezone.now()
        deleted_dest = 'core' + os.sep + 'source' + os.sep + 'deleted_' + object.plugin_source.source_hash + \
            '_' + str(datetime.timestamp(object.plugin_source.upload_time))

        log_json: dict = {
            'log_datetime': datetime.timestamp(deleted_time),
            'source_dest': object.plugin_source.source_dest,
            'source_hash': object.plugin_source.source_hash,
            'upload_time': object.plugin_source.upload_time.strftime("%m/%d/%Y, %H:%M:%S"),
            'upload_user_username': object.plugin_source.upload_user.username,
            'upload_user_email': object.plugin_source.upload_user.email,
            'source_file_hash': json.loads(object.plugin_source.source_file_hash),
            'username': user.username,
            'user_email': user.email,
            'deleted_dest': deleted_dest
        }
        write_log(LogType.DELETE, object.plugin_source, log_json)

        shutil.move(source_dest, deleted_dest)

        object.plugin_source.source_hash = 'deleted_' + object.plugin_source.source_hash
        object.plugin_source.source_dest = deleted_dest
        object.plugin_source.save()

        return super().delete(request, *args, **kwargs)
