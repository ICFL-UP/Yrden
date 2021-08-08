from os import name
from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.PluginIndexView.as_view(), name='index'),
    path('plugin/', views.PluginCreateView.as_view(),
         name='plugin_create_form'),
    path('plugin/<int:pk>', views.PluginDetailView.as_view(), name='plugin_detail'),
    path('plugin/<int:pk>/update', views.PluginUpdateView.as_view(), name='plugin_update'),
    path('plugin/<int:pk>/delete', views.PluginDeleteView.as_view(), name='plugin_delete'),
]
