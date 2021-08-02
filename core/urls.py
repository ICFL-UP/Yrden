from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.PluginIndexView.as_view(), name='index'),
    path('<int:pk>/', views.PluginDetailView.as_view(), name='detail'),
    path('plugin/', views.PluginCreateView.as_view(),
         name='plugin_create_form'),
]
