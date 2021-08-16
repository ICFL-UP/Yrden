import subprocess
import os
import shutil

from django.views.generic import ListView, DetailView, CreateView
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView, UpdateView
from django.shortcuts import redirect
from django.urls import reverse

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

    def form_valid(self, form, plugin_formset):
        self.object = form.save(commit=False)
        self.object.save()
        # saving Plugin Instance
        plugin = plugin_formset.save(commit=False)
        plugin = self.object
        plugin.save()
        return redirect(reverse("core:index"))

    def form_invalid(self, form, plugin_formset):
        return self.render_to_response(
            self.get_context_data(form=form,
                                  product_meta_formset=plugin_formset
                                  )
        )

# class PluginCreateView(CreateView):
#     model = Plugin
#     template_name_suffix = '_create_form'
#     form_class = PluginCreateForm
#     success_url = reverse_lazy('core:index')

#     def form_valid(self, form: PluginCreateForm) -> HttpResponse:
#         ZIP_NAME = 'plugin_zip_file'

#         plugin = form.save(commit=False)
#         plugin.hash_name = form.cleaned_data['hash_name']
        
#         # Create venv
#         # TODO: need to add functionality for specifying different python versions
#         plugin.plugin_dest = 'core' + os.sep + 'plugin' + os.sep + form.cleaned_data['hash_name']
#         venv_dest = plugin.plugin_dest + os.sep + '.venv'
#         subprocess.run(['python', '-m', 'virtualenv', venv_dest, '-p', 'python'])

#         # Install requirements
#         python = venv_dest + os.sep + 'bin' + os.sep + 'python'
#         requirements = plugin.plugin_dest + os.sep + 'requirements.txt'
#         subprocess.run([python, '-m', 'pip', 'install', '-r', requirements])

#         plugin.save()
#         return super().form_valid(form)


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

    def delete(self, request, *args: str, **kwargs):
        object = self.get_object()
        shutil.rmtree('core' + os.sep + 'plugin' + os.sep + object.hash_name)
        # os.rmdir('core' + os.sep + 'plugin' + os.sep + object.hash_name)
        return super().delete(request, *args, **kwargs)