from django.urls import path, re_path, register_converter

from integration_badges.views import *

# Define our custom URLs
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
     path(r'v1/roadmaps/',
          Roadmap_Detail_v1.as_view(),
          name='roadmap-v1-all'),

     path(r'v1/roadmap/<str:roadmap_id>/',
          Roadmap_Detail_v1.as_view(),
          name='roadmap-v1-id'),

     path(r'v1/badges/',
          Badge_v1.as_view(),
          name='badges-v1-all'),

     path(r'v1/badge/<str:badge_id>/',
          Badge_v1.as_view(),
          name='badges-v1-id'),

     path(r'v1/badge/<str:badge_id>/tasks/',
          Badge_Task_v1.as_view(),
          name='badge-tasks-v1-id'),

     path(r'v1/resources/',
          Resource_List_v1.as_view(),
          name='resources-list-v1-all'),

     path(r'v1/resource/<str:info_resourceid>/',
          Resource_v1.as_view(),
          name='resource-v1-id'),

     path(r'v1/resource/<str:info_resourceid>/roadmap/<str:roadmap_id>/badges/',
          Resource_Roadmap_Badges_v1.as_view(),
          name='resource-roadmap-badges-v1-id'),

     path(r'v1/resource/<str:info_resourceid>/roadmap/<str:roadmap_id>/badge/<str:integration_badge_id>/',
          Resource_Roadmap_Badge_v1.as_view(),
          name='resource-roadmap-badge-v1-id'),

     path(r'v1/resource/<str:info_resourceid>/roadmap/<str:roadmap_id>/badge/<str:integration_badge_id>/tasks/',
          Resource_Roadmap_Badge_Tasks_v1.as_view(),
          name='resource-roadmap-badge-tasks-v1-id'),

     path(r'v1/resource/<str:info_resourceid>/roadmap/<str:roadmap_id>/badge/<str:badge_id>/workflow/<str:badge_workflow_status>/',
          Resource_Badge_Status_v1.as_view(),
          name='resource-badge-status-v1-id'),

     path(r'v1/resource/<str:info_resourceid>/roadmap/<str:roadmap_id>/badge/<str:badge_id>/task/<str:task_id>/workflow/<str:badge_task_workflow_status>/',
          Resource_Badge_Task_Status_v1.as_view(),
          name='resource-badge-task-status-v1-id'),

     path(r'v1/files/<str:file_id>/',
          DatabaseFile_v1.as_view(),
          name='database-file-v1-id'),

]
