"""Operations_Warehouse_Django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings as django_settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from access_django_user_admin import views


urlpatterns = [
    path('', RedirectView.as_view(url='/docs/') ),
    path('accounts/', include('allauth.urls') ),
    path('admin/', admin.site.urls),
    path('docs/', include('web.urls') ),
#
    path('wh2/state/', include('warehouse_state.urls')),
    path('wh2/allocations/', include('allocations.urls') ),
    path('wh2/cider/', include('cider.urls') ),
    path('wh2/integration_badges/', include('integration_badges.urls') ),
    path('wh2/glue2/', include('glue2.urls') ),
    path('wh2/news/', include('news.urls') ),
    path('wh2/resource/', include('resource_v4.urls') ),

# Optional UI:
    path('wh2/api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('wh2/api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('wh2/api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('access_django_user_admin/', include('access_django_user_admin.urls')),
]
