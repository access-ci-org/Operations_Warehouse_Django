import traceback
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from django.db import transaction
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Q

from integration_badges.models import *
from integration_badges.serializers import *
from cider.serializers import *

from warehouse_tools.exceptions import MyAPIException
from warehouse_tools.responses import MyAPIResponse

from drf_spectacular.utils import extend_schema, OpenApiParameter
import logging
from .permissions import IsRoadmapMaintainer, IsCoordinator, IsImplementer, ReadOnly

log = logging.getLogger(__name__)

badging_types = ('Compute', 'Storage')  # Expand as more roadmaps with badges are rolled out
badging_statuses = ('coming soon', 'friendly', 'pre-production', 'production', 'post-production')
badging_filter = Q(cider_type__in=badging_types) & Q(latest_status__in=badging_statuses) & Q(
    project_affiliation__icontains='ACCESS')


# _Detail_ includes all fields from a Model
# _Full_ includes fields from a model and dependent Models (i.e. roadmap badges, badge tasks, ..)
# _Min_ serializers include minimum set of fields

class Roadmap_Full_v1(GenericAPIView):
    '''
    Integration Roadmap(s) and related Badge details View
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = Roadmap_Full_Serializer

    def get(self, request, format=None, **kwargs):
        roadmap_id = self.kwargs.get('roadmap_id')
        if roadmap_id:
            try:
                items = Roadmap.objects.get(pk=roadmap_id)
                many = False
            except Roadmap.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified roadmap_id not found')
        else:
            items = Roadmap.objects.all()
            many = True

        serializer = self.serializer_class(items, context={'request': request}, many=many)
        return MyAPIResponse({'results': serializer.data})


class Badge_Full_v1(GenericAPIView):
    '''
    Integration Badge(s) and pre-requisites
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = Badge_Full_Serializer

    def get(self, request, format=None, **kwargs):
        badge_id = self.kwargs.get('badge_id')
        if badge_id:
            try:
                item = Badge.objects.get(pk=badge_id)
                many = False
            except Badge.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified badge_id not found')
        else:
            item = Badge.objects.all()
            many = True

        serializer = self.serializer_class(item, context={'request': request}, many=many)
        return MyAPIResponse({'results': serializer.data})


class Badge_Task_Full_v1(GenericAPIView):
    '''
    Retrieve an Integration Task by ID
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = Badge_Task_Full_Serializer

    def get(self, request, *args, **kwargs):
        badge_id = kwargs.get('badge_id')
        if not badge_id:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Badge ID is required')

        badge_tasks = Badge_Task.objects.filter(badge_id=badge_id).order_by('sequence_no')
        if badge_tasks.exists():
            serializer = self.serializer_class(badge_tasks, context={'request': request}, many=True)
            return MyAPIResponse({'results': serializer.data})
        else:
            # Return empty list if no tasks found, not an error
            return MyAPIResponse({'results': []})


class Resources_Eligible_List_v1(GenericAPIView):
    '''
    Integration eligible CiDeR resources, which could be, are, or were integrated, but haven't been retired
    
    Based only on CiDeR since they may not have enrolled in a roadmap yet
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderInfrastructure_Summary_Serializer

    @extend_schema(
        responses=CiderInfrastructure_Summary_Serializer,
    )
    def get(self, request, format=None, **kwargs):
        badging_statuses = ('coming soon', 'friendly', 'pre-production', 'production', 'post-production')
        # Will expand once more roadmaps with badges are rolled out
        badging_types = ('Compute', 'Storage')

        resources = CiderInfrastructure.objects.filter(badging_filter)
        serializer = self.serializer_class(resources, context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})


class Resource_Full_v1(GenericAPIView):
    '''
    Resource full details, including roadmaps, badges, and badge status
    '''
    permission_classes = (AllowAny,)
    # permission_classes = [IsCoordinator | (IsAuthenticated & ReadOnly)]
    renderer_classes = (JSONRenderer,)
    serializer_class = Resource_Full_Serializer

    def get(self, request, format=None, **kwargs):
        info_resourceid = kwargs.get('info_resourceid')
        if not info_resourceid:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Info_ResourceID is required')

        try:
            resource = CiderInfrastructure.objects.get(Q(info_resourceid=info_resourceid) & badging_filter)
        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND,
                                 detail='Specified Info_ResourceID does not exist or is not eligible')

        serializer = self.serializer_class(resource, context={'request': request}, many=False)
        return MyAPIResponse({'results': serializer.data})


class Resource_Roadmap_Enrollments_v1(GenericAPIView):
    '''
    Resource roadmap and roadmap badge enrollments
    '''
    permission_classes = (AllowAny,)
    # permission_classes = [IsCoordinator | (IsAuthenticated & ReadOnly)]
    renderer_classes = (JSONRenderer,)
    serializer_class = Resource_Enrollments_Serializer

    @extend_schema(
        responses=Resource_Enrollments_Response_Serializer,
    )
    def post(self, request, format=None, **kwargs):
        info_resourceid = kwargs.get('info_resourceid')
        if not info_resourceid:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Info_ResourceID is required')
        roadmap_id = kwargs.get('roadmap_id')
        if not roadmap_id:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='RoadmapID is required')
        try:
            resource = CiderInfrastructure.objects.get(Q(info_resourceid=info_resourceid) & badging_filter)
            roadmap = Roadmap.objects.get(pk=roadmap_id)
        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND,
                                 detail='Specified Info_ResourceID does not exist or is not eligible')
        except Roadmap.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified RoadmapID not found')

        message = ''
        enroll_badges = []
        unenroll_badges = []

        # Enroll Resource in Roadmap if not already enrolled
        try:
            resource_roadmap = Resource_Roadmap.objects.get(info_resourceid=info_resourceid, roadmap=roadmap)
        except Resource_Roadmap.DoesNotExist:
            resource_roadmap = None
        except Exception as exc:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='{}: {}'.format(type(exc).__name__, exc))
        if not resource_roadmap:
            try:
                resource_roadmap = Resource_Roadmap(info_resourceid=info_resourceid, roadmap=roadmap).save()
                message += f'Enrolled roadmap={roadmap.name}'
            except Exception as exc:
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='{}: {}'.format(type(exc).__name__, exc))

        # Check that badge_ids were specified
        raw_badge_ids = request.data.get('badge_ids')
        if not raw_badge_ids or type(raw_badge_ids) is not list:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Missing BadgeIDs or not a list')
        new_badge_ids = list(str(id) for id in raw_badge_ids)

        # Verify that each badge is available in the roadmap
        for id in new_badge_ids:
            try:
                new_roadmap_badge = Roadmap_Badge.objects.get(roadmap_id=roadmap_id, badge_id=id)
            except Roadmap_Badge.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND,
                                     detail=f'Badge.ID ({id}) is not availabe in roadmap ({roadmap_id})')

        # Retrieve current badges
        try:
            cur_badges = Resource_Badge.objects.filter(info_resourceid=info_resourceid, roadmap_id=roadmap_id)
            cur_badge_ids = [str(id) for id in cur_badges.values_list('badge_id', flat=True)]
        except Exception as exc:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='{}: {}'.format(type(exc).__name__, exc))

        # Check and enroll in badges
        for id in new_badge_ids:
            if id not in cur_badge_ids:
                try:
                    Resource_Badge(info_resourceid=info_resourceid, roadmap_id=roadmap_id, badge_id=id).save()
                except Exception as exc:
                    raise MyAPIException(code=status.HTTP_400_BAD_REQUEST,
                                         detail='{}: {}'.format(type(exc).__name__, exc))
                enroll_badges.append(id)

        # Check and unenroll in badges
        for cur in cur_badges:
            if str(cur.badge_id) not in new_badge_ids:
                try:
                    cur.delete()
                except Exception as exc:
                    raise MyAPIException(code=status.HTTP_400_BAD_REQUEST,
                                         detail='{}: {}'.format(type(exc).__name__, exc))
                unenroll_badges.append(str(cur.badge_id))

        if enroll_badges:
            message += '; ' if message else ''
            message += f'Enrolled badges=({",".join(enroll_badges)})'
        if unenroll_badges:
            message += '; ' if message else ''
            message += f'Unenrolled badges=({",".join(unenroll_badges)})'
        return MyAPIResponse({'message': message})


class Resource_Badge_Status_v1(GenericAPIView):
    '''
    Record Badge Status
    '''
    permission_classes = (AllowAny,)
    # permission_classes = [IsCoordinator | (IsAuthenticated & ReadOnly)]
    renderer_classes = (JSONRenderer,)
    serializer_class = Resource_Workflow_Post_Serializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='badge_workflow_status',
                description='Workflow status',
                type=str,
                required=True,
                location=OpenApiParameter.PATH,
                enum=BadgeWorkflowStatus,
                default=BadgeWorkflowStatus.PLANNED
            )
        ],
        request=Resource_Workflow_Post_Serializer,
    )
    def post(self, request, badge_workflow_status, *args, **kwargs):
        info_resourceid = kwargs.get('info_resourceid')
        roadmap_id = kwargs.get('roadmap_id')
        badge_id = kwargs.get('badge_id')
        if not info_resourceid or not roadmap_id or not badge_id or not badge_workflow_status:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST,
                                 detail='Info_ResourceID, Roadmap ID, Badge ID and status are required')

        try:
            resource = CiderInfrastructure.objects.get(info_resourceid=info_resourceid)
            roadmap = Roadmap.objects.get(pk=roadmap_id)
            badge = Badge.objects.get(pk=badge_id)
            resource_badge = Resource_Badge.objects.get(info_resourceid=info_resourceid, roadmap=roadmap, badge=badge)
        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified resource not found')
        except Roadmap.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified roadmap not found')
        except Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified badge not found')
        except Resource_Badge.DoesNotExist:
            resource_badge = Resource_Badge(
                info_resourceid=info_resourceid,
                roadmap=roadmap,
                badge=badge
            )
            resource_badge.save()

        updated_by = request.data.get('status_updated_by')
        if not updated_by:
            updated_by = get_current_username()

        workflow = Resource_Badge_Workflow(
            info_resourceid=info_resourceid,
            roadmap=roadmap,
            badge=badge,
            status=badge_workflow_status,
            status_updated_by=updated_by,
            comment=request.data.get('comment')
        )
        workflow.save()

        return MyAPIResponse({
            'message': 'Badge marked as %s' % badge_workflow_status,
            'status_updated_at': workflow.status_updated_at
        })

class Resource_Badge_Task_Status_v1(GenericAPIView):
    '''
    Record Badge Task Status
    '''
    permission_classes = (AllowAny,)
    # permission_classes = [IsCoordinator | (IsAuthenticated & ReadOnly)]
    renderer_classes = (JSONRenderer,)
    serializer_class = Resource_Workflow_Post_Serializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='badge_task_workflow_status',
                description='Filter by status',
                type=str,
                required=True,
                location=OpenApiParameter.PATH,
                enum=BadgeTaskWorkflowStatus,
                default=BadgeTaskWorkflowStatus.COMPLETED
            )
        ],
        request=Resource_Workflow_Post_Serializer,
    )
    def post(self, request, badge_task_workflow_status, *args, **kwargs):
        info_resourceid = kwargs.get('info_resourceid')
        roadmap_id = kwargs.get('roadmap_id')
        badge_id = kwargs.get('badge_id')
        task_id = kwargs.get('task_id')
        if not info_resourceid or not roadmap_id or not badge_id or not task_id or not badge_task_workflow_status:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST,
                                 detail='Info_ResourceID, Roadmap ID, Badge ID, Task ID and status are required')

        try:
            resource = CiderInfrastructure.objects.get(info_resourceid=info_resourceid)
            roadmap = Roadmap.objects.get(pk=roadmap_id)
            badge = Badge.objects.get(pk=badge_id)
            task = Task.objects.get(pk=task_id)
            resource_badge = Resource_Badge.objects.get(info_resourceid=info_resourceid, roadmap=roadmap, badge=badge)
            badge_task = Badge_Task.objects.get(badge=badge, task=task)
        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified resource not found')
        except Roadmap.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified roadmap not found')
        except Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified badge not found')
        except Task.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified task not found')
        except Resource_Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND,
                                 detail='Specified resource-badge relationship not found')
        except Badge_task.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified badge-task relationship not found')

        updated_by = request.data.get('status_updated_by')
        if not updated_by:
            updated_by = get_current_username()
        workflow = Resource_Badge_Task_Workflow(
            info_resourceid=info_resourceid,
            roadmap=roadmap,
            badge=badge,
            task=task,
            status=badge_task_workflow_status,
            status_updated_by=updated_by,
            comment=request.data.get('comment')
        )
        workflow.save()

        return MyAPIResponse({
            'message': 'Badge task marked as %s' % badge_task_workflow_status,
            'status_updated_at': workflow.status_updated_at
        })


class Resource_Roadmap_Badges_Status_v1(GenericAPIView):
    '''
    Retrieve all or one resource badge(s) and their status
    '''
    permission_classes = (AllowAny,)
    # permission_classes = [IsCoordinator | (IsAuthenticated & ReadOnly)]
    renderer_classes = (JSONRenderer,)
    serializer_class = Resource_Roadmap_Serializer

    def get(self, request, format=None, **kwargs):
        info_resourceid = kwargs.get('info_resourceid')
        roadmap_id = kwargs.get('roadmap_id')
        badge_id = kwargs.get('badge_id')
        if not info_resourceid:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Info_ResourceID is required')

        try:
            resource = CiderInfrastructure.objects.get(info_resourceid=info_resourceid)
            roadmap = Roadmap.objects.get(pk=roadmap_id)
            resource_roadmap = Resource_Roadmap.objects.get(info_resourceid=info_resourceid, roadmap_id=roadmap_id)

        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified Info_ResourceID not found')
        except Roadmap.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified RoadmapID not found')
        except Resource_Roadmap.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND,
                                 detail='Specified resource-roadmap relationship not found not found')

        if badge_id:
            try:
                resource_badge = Resource_Badge.objects.get(info_resourceid=info_resourceid, roadmap_id=roadmap_id,
                                                            badge_id=badge_id)
                badge_status = {
                    'id': resource_badge.id,
                    'info_resourceid': resource_badge.info_resourceid,
                    'roadmap_id': resource_badge.roadmap_id,
                    'badge_id': resource_badge.badge_id,
                    'badge_access_url': resource_badge.badge_access_url,
                    'badge_access_url_label': resource_badge.badge_access_url_label,
                    'status': resource_badge.status,
                    'status_updated_by': resource_badge.workflow.status_updated_by if resource_badge.workflow else None,
                    'status_updated_at': resource_badge.workflow.status_updated_at if resource_badge.workflow else None,
                    'comment': resource_badge.workflow.comment if resource_badge.workflow else None
                }
            except Resource_Badge.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND,
                                     detail='Specified resource-roadmap-badge relationship not found')
            return MyAPIResponse({'results': badge_status})

        roadmap_badges = Roadmap_Badge.objects.filter(roadmap_id=roadmap_id)
        roadmap_badge_ids = [roadmap_badge.badge_id for roadmap_badge in roadmap_badges]
        resource_badges = Resource_Badge.objects.filter(info_resourceid=info_resourceid, roadmap_id=roadmap_id,
                                                        badge_id__in=roadmap_badge_ids)
        badges_status = []
        for resource_badge in resource_badges:
            badge_status = {
                'id': resource_badge.id,
                'info_resourceid': resource_badge.info_resourceid,
                'roadmap_id': resource_badge.roadmap_id,
                'badge_id': resource_badge.badge_id,
                'badge_access_url': resource_badge.badge_access_url,
                'badge_access_url_label': resource_badge.badge_access_url_label,
                'status': resource_badge.status,
                'status_updated_by': resource_badge.workflow.status_updated_by if resource_badge.workflow else None,
                'status_updated_at': resource_badge.workflow.status_updated_at if resource_badge.workflow else None,
                'comment': resource_badge.workflow.comment if resource_badge.workflow else None
            }
            badges_status.append(badge_status)
        return MyAPIResponse({'results': badges_status})


class Resource_Roadmap_Badge_Tasks_Status_v1(GenericAPIView):
    '''
    Retrieve details of a specific resource, including roadmaps and their badges.
    It also includes the list of badge statuses of the badges that are at least planned.
    '''
    permission_classes = (AllowAny,)
    # permission_classes = [IsCoordinator | (IsAuthenticated & ReadOnly)]
    renderer_classes = (JSONRenderer,)
    serializer_class = Resource_Roadmap_Serializer

    def get(self, request, format=None, **kwargs):
        info_resourceid = kwargs.get('info_resourceid')
        roadmap_id = kwargs.get('roadmap_id')
        badge_id = kwargs.get('badge_id')
        if not info_resourceid or not roadmap_id or not badge_id:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST,
                                 detail='Info_ResourceID, RoadmapID and BadgeID are required')

        try:
            resource = CiderInfrastructure.objects.get(info_resourceid=info_resourceid)
            roadmap = Roadmap.objects.get(pk=roadmap_id)
            badge = Badge.objects.get(pk=badge_id)
        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified Info_ResourceID not found')
        except Roadmap.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified RoadmapID not found')
        except Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified BadgeID not found not found')

        task_status = []
        badge_tasks = Badge_Task.objects.filter(badge_id=badge_id)
        for badge_task in badge_tasks:
            task_workflow = Resource_Badge_Task_Workflow.objects.filter(
                info_resourceid=info_resourceid,
                roadmap_id=roadmap_id,
                badge_id=badge_id,
                task_id=badge_task.task_id
            ).order_by('-status_updated_at').first()
            if task_workflow is not None:
                task_status.append({
                    "task_id": badge_task.task_id,
                    "task_name": badge_task.task.name,
                    "status": task_workflow.status,
                    "status_updated_by": task_workflow.status_updated_by,
                    "status_updated_at": task_workflow.status_updated_at
                })
            else:
                task_status.append({
                    "task_id": badge_task.task_id,
                    "task_name": badge_task.task.name,
                    "status": None,
                    "status_updated_by": None,
                    "status_updated_at": None
                })
        return MyAPIResponse({'results': task_status})


class DatabaseFile_v1(GenericAPIView):
    '''
    Retrieve tasks of a specific badge.
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = DatabaseFile_Serializer

    def get(self, request, *args, **kwargs):
        file_id = kwargs.get('file_id')
        if not file_id:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='File ID is required')

        try:
            file = DatabaseFile.objects.get(pk=file_id)
        except DatabaseFile.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='File not found')

        response = HttpResponse(file.file_data, content_type=file.content_type)
        response['Content-Disposition'] = 'inline; filename="%s"' % file.file_name

        return response
