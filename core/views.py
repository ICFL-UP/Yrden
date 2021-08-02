from django.db.models.query import QuerySet
from django.http.response import HttpResponse
from django.views import generic

from .models import Plugin
from .forms import PluginCreateForm

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
        # TODO: handle logic for installing the plugin
        return super().form_valid(form)


# This should be moved out (only using this for testing until the crontabs are set up fully)
# =============================================

def walk_plugins(plugin: Plugin):
    import os
    import subprocess

    dir = 'core/plugin'
    for fname in os.listdir(dir):
        main = dir + os.sep + fname + os.sep + 'main.py'
        if fname.lower() == str(plugin.name).lower() and os.path.isfile(main):
            process = subprocess.run(['python', main], check=True, stdout=subprocess.PIPE)
            output = process.stdout


qs = Plugin.objects.all()
for plugin in qs:
    walk_plugins(plugin)

# =============================================