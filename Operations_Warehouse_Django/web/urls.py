from django.urls import include, path, re_path

from web import views

app_name = 'web'
urlpatterns = [
    path('', views.index, name='index'),
]
