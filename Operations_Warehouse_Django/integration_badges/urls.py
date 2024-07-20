from django.urls import path, re_path

from integration_badges.views import *

# Define our custom URLs
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
    path(r'v1/roadmap/', Integration_Roadmap_v1.as_view(), name='integration-roadmap-v1-all'),
    path(r'v1/roadmap/<str:integration_roadmap_id>/', Integration_Roadmap_v1.as_view(), name='integration-roadmap-v1-id'),
    path(r'v1/badge/', Integration_Badge_v1.as_view(), name='integration-badges-v1-all'),
    path(r'v1/badge/<str:integration_badge_id>/', Integration_Badge_v1.as_view(), name='integration-badges-v1-id'),
    path(r'v1/resources/', Integration_Resource_List_v1.as_view(), name='integration-resources-list-v1-all'),
    path(r'v1/resource/<str:cider_resource_id>/', Integration_Resource_v1.as_view(), name='integration-resource-v1-id'),
    path(r'v1/task/<str:integration_badge_id>/', Integration_Task_v1.as_view(), name='integration-tasks-v1-id'),
    path(r'v1/resource/<str:cider_resource_id>/<str:integration_badge_id>/plan', 
         Integration_Resource_Badge_Plan_v1.as_view(), name='integration-resource-badge-v1-id-plan'),
    path(r'v1/resource/<str:cider_resource_id>/<str:integration_badge_id>/unplan', 
         Integration_Resource_Badge_Unplan_v1.as_view(), name='integration-resource-badge-v1-id-unplan'),
    path(r'v1/resource/<str:cider_resource_id>/state', Integration_Resource_Badge_Status_v1.as_view(), name='integration-resource-badge-status-v1-id'),
    path(r'v1/resource/<str:cider_resource_id>/<str:integration_badge_id>/task_completed', 
         Integration_Resource_Badge_Task_Completed_v1.as_view(), name='integration-resource-badge-task_completed-v1-id'),
]
