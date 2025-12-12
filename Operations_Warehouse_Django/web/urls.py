from django.urls import include, path, re_path

from web import views

app_name = 'web'
urlpatterns = [
    path('dump.html', views.Debug_Detail.as_view(), name='debug-detail'),
    path('', views.index, name='index'),
]
