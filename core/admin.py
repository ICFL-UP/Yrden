from django.contrib import admin
from django.http.request import HttpRequest
from django_admin_inline_paginator.admin import TabularInlinePaginated

from .models import Plugin, PluginSource, PluginRun


class SoftDeletionAdmin(admin.ModelAdmin):
    def get_queryset(self, request: HttpRequest):
        qs = self.model.all_objects

        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def delete_model(self, request: HttpRequest, obj) -> None:
        obj.hard_delete()


class PluginInline(admin.TabularInline):
    model = Plugin
    fk_name = 'plugin_source'


@admin.register(PluginSource)
class PluginSourceAdmin(SoftDeletionAdmin):
    inlines = [
        PluginInline
    ]


class PluginRunInline(TabularInlinePaginated):
    model = PluginRun
    fk_name = 'plugin'
    extra = 0
    per_page = 15


@admin.register(Plugin)
class PluginAdmin(SoftDeletionAdmin):
    inlines = [
        PluginRunInline
    ]
