from django.contrib import admin
from django.http.request import HttpRequest

from .models import Plugin, PluginSource, PluginRun


class PluginInline(admin.TabularInline):
    model = Plugin
    fk_name = 'plugin_source'


@admin.register(PluginSource)
class PluginSourceAdmin(admin.ModelAdmin):
    inlines = [
        PluginInline
    ]


class PluginRunInline(admin.TabularInline):
    model = PluginRun
    fk_name = 'plugin'
    extra = 0


@admin.register(Plugin)
class PluginAdmin(admin.ModelAdmin):
    inlines = [
        PluginRunInline
    ]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_delete_permission(self, request, obj=None):
        return False
