# roadmap_pivot/urls.py
from django.urls import path
from .views import RoadmapResourceBadgesView

urlpatterns = [
    path('', RoadmapResourceBadgesView.as_view(), name='roadmap-pivot'),
]