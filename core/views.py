from django.db.models.query import QuerySet
from django.views import generic

from .models import Plugin
from .forms import PluginCreateForm

from .plugin.plugin_mount import PluginMount

pm = PluginMount()

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
