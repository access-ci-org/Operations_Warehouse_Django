# roadmap_pivot/urls.py
from django.urls import path
from .views import RoadmapResourceBadgesView, GroupBadgeStatusView, RoadmapResourceBadgesAPI, GroupBadgeStatusAPI


urlpatterns = [
    path(r'v1/resource_pivot/', RoadmapResourceBadgesView.as_view(), name='resource-pivot'),
    path(r'v1/resource_pivot/json/', RoadmapResourceBadgesAPI.as_view(), name='resource-pivot-json'),
    path(r'v1/group_pivot/', GroupBadgeStatusView.as_view(), name='group-pivot'),
    path(r'v1/group_pivot/json/', GroupBadgeStatusAPI.as_view(), name='group-pivot-json'),
]