from django.urls import path

from . import views

host = 'localhost'
port = '8000'
app_name = 'core'

print('Views for core')
print(f'http://{host}:{port}/{app_name}/')
print(f'http://{host}:{port}/{app_name}/1/')
print()

urlpatterns = [
    path('', views.PluginIndexView.as_view(), name='index'),
    path('<int:pk>/', views.PluginDetailView.as_view(), name='detail'),
    path('plugin/', views.PluginCreateView.as_view(),
         name='plugin_create_form'),
]
