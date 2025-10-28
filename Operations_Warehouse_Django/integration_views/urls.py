# roadmap_pivot/urls.py
from django.urls import path
from .views import RoadmapResourceBadgesView

urlpatterns = [
    path(r'v1/resource_pivot/', RoadmapResourceBadgesView.as_view(), name='resource-pivot'),
]