from django.urls import path, re_path, register_converter

from integration_badges.views import *

# Define our custom URLs
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
     path(r'v1/roadmaps/',
          Roadmap_Full_v1.as_view(), name='roadmaps-full-v1'),

     path(r'v1/roadmap/<str:roadmap_id>/',
          Roadmap_Full_v1.as_view(), name='roadmap-id-v1'),

     path(r'v1/badges/',
          Badge_Full_v1.as_view(), name='badges-full-v1'),

     path(r'v1/roadmap_review/',
          Roadmap_Review_v1.as_view(), name='roadmaps-review-v1'),

     path(r'v1/roadmap_review/<str:roadmap_id>/',
          Roadmap_Review_v1.as_view(), name='roadmap-id-review-v1'),

     path(r'v1/badge_review/',
          Badge_Review_v1.as_view(), name='badges-review-v1'),

     path(r'v1/badge_review/<str:badge_id>/',
          Badge_Review_v1.as_view(), name='badge-id-review-v1'),

     path(r'v1/badge_verification/',
          Badge_Verification_v1.as_view(), name='badges-verification-v1'),

     path(r'v1/badge/<str:badge_id>/',
          Badge_Full_v1.as_view(), name='badge-id-v1'),

     path(r'v1/badge/<str:badge_id>/tasks/',
          Badge_Task_Full_v1.as_view(), name='badge-id-tasks-v1'),

     path(r'v1/resources/',
          Resources_Eligible_List_v1.as_view(), name='resources-eligible-list-v1'),

     path(r'v1/resource/<str:info_resourceid>/',
          Resource_Full_v1.as_view(), name='resource-id-full-v1'),

     path(r'v1/resource/<str:info_resourceid>/roadmap/<str:roadmap_id>/enrollments/',
          Resource_Roadmap_Enrollments_v1.as_view(), name='resource-id-roadmap-id-enrollments-v1'),

     path(r'v1/resource_roadmap_badges/',
          Resource_Roadmap_Badges_Status_v1.as_view(), name='resource-id-roadmap-id-badge-id-status-v1'),

     path(r'v1/resource_roadmap_badge_tasks/',
          Resource_Roadmap_Badge_Tasks_Status_v1.as_view(), name='resource-id-roadmap-id-badge-id-tasks-status-id'),

     path(r'v1/resource_roadmap_badge_logs/',
          Resource_Roadmap_Badge_Log_v1.as_view(), name='resource-roadmap-badge-log-v1'),

     path(r'v1/resource/<str:info_resourceid>/roadmap/<str:roadmap_id>/badge/<str:badge_id>/workflow/<str:badge_workflow_status>/',
          Resource_Badge_Status_v1.as_view(), name='resource-id-roadmap-id-badge-id-workflow-v1'),

     path(r'v1/resource/<str:info_resourceid>/roadmap/<str:roadmap_id>/badge/<str:badge_id>/task/<str:task_id>/workflow/<str:badge_task_workflow_status>/',
          Resource_Badge_Task_Status_v1.as_view(), name='resource-id-roadmap-id-badge-id-task-id-workflow-v1'),

     path(r'v1/files/<str:file_id>/',
          DatabaseFile_v1.as_view(), name='database-file-id-v1'),
]
