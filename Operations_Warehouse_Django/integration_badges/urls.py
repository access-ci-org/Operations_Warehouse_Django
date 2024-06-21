from django.urls import path, re_path

from integration_badges.views import *

# Define our custom URLs
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
    path(r'v1/roadmap/', Integration_Roadmap_v1.as_view(), name='integration-roadmap-v1-all'),
    path(r'v1/roadmap/<str:integration_roadmap_id>/', Integration_Roadmap_v1.as_view(), name='integration-roadmap-v1-id')
]
