# roadmap_pivot/urls.py
from django.urls import path
from .views import RoadmapResourceBadgesView, GroupBadgeStatusView


urlpatterns = [
    path(r'v1/resource_pivot/', RoadmapResourceBadgesView.as_view(), name='resource-pivot'),
<<<<<<< HEAD
=======
    path(r'v1/group_pivot/', GroupBadgeStatusView.as_view(), name='group-pivot'),
>>>>>>> 5dc18fa (ctt 727 adding rp group view v1)
]