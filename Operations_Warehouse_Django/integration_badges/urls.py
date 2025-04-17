from django.urls import path, re_path, register_converter

from integration_badges.views import *

# Define our custom URLs
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
     path(r'v1/roadmaps/',
          Integration_Roadmap_v1.as_view(),
          name='integration-roadmap-v1-all'),

     path(r'v1/roadmap/<str:integration_roadmap_id>/',
          Integration_Roadmap_v1.as_view(),
          name='integration-roadmap-v1-id'),

     path(r'v1/badges/',
          Integration_Badge_v1.as_view(),
          name='integration-badges-v1-all'),

     path(r'v1/badge/<str:integration_badge_id>/',
          Integration_Badge_v1.as_view(),
          name='integration-badges-v1-id'),

     path(r'v1/badge/<str:integration_badge_id>/tasks/',
          Integration_Task_v1.as_view(),
          name='integration-tasks-v1-id'),

     path(r'v1/resources/',
          Integration_Resource_List_v1.as_view(),
          name='integration-resources-list-v1-all'),

     path(r'v1/resource/<str:info_resourceid>/',
          Integration_Resource_v1.as_view(),
          name='integration-resource-v1-id'),

     path(r'v1/resource/<str:info_resourceid>/roadmap/<str:roadmap_id>/badge/<str:integration_badge_id>/workflow/<str:badge_workflow_status>/',
          Integration_Resource_Badge_Status_v1.as_view(),
          name='integration-resource-badge-status-v1-id'),

     path(r'v1/resource/<str:info_resourceid>/roadmap/<str:roadmap_id>/badge/<str:integration_badge_id>/task/<str:integration_task_id>/workflow/<str:badge_task_workflow_status>/',
          Integration_Resource_Badge_Task_Status_v1.as_view(),
          name='integration-resource-badge-task-status-v1-id'),

     path(r'v1/files/<str:file_id>/',
          DatabaseFile_v1.as_view(),
          name='database-file-v1-id'),

]
