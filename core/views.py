from django.shortcuts import render, get_object_or_404
from django.db.models.query import QuerySet
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.urls.base import reverse_lazy
from django.views import generic
from django.utils import timezone

from .models import Plugin

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
    fields = ['name', 'interval', 'should_run']
