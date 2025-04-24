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


class Roadmap_Detail_v1(GenericAPIView):
    '''
        Integration Roadmap and related Badge details View
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = Roadmap_Detail_Serializer

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


class Badge_v1(GenericAPIView):
    '''
    Retrieve an Integration Badge by ID.
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


class Resource_List_v1(GenericAPIView):
    '''
    Retrieve all resources, including badges that are at least planned.
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderInfrastructure_Summary_Serializer
    # serializer_class = Resource_List_Serializer

    def get(self, request, format=None, **kwargs):
        badging_statuses = ('coming soon', 'friendly', 'pre-production', 'production', 'post-production')
        badging_types = ('Compute', 'Storage')

        resources = CiderInfrastructure.objects.filter(
            Q(cider_type__in=badging_types) & Q(latest_status__in=badging_statuses) &
            Q(project_affiliation__icontains='ACCESS'))

        serializer = self.serializer_class(resources, context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})


class Resource_v1(GenericAPIView):
    '''
    Retrieve details of a specific resource, including roadmaps, badges, and badge status.
    '''
    permission_classes = (AllowAny,)
    #permission_classes = [IsCoordinator | (IsAuthenticated & ReadOnly)]
    renderer_classes = (JSONRenderer,)
    serializer_class = Integration_Resource_Serializer

    def get(self, request, format=None, **kwargs):
        info_resourceid = kwargs.get('info_resourceid')
        if not info_resourceid:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Info_ResourceID is required')

        try:
            item = CiderInfrastructure.objects.get(info_resourceid=info_resourceid)
        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified Info_ResourceID not found')

#        roadmaps = Resource_Roadmap.objects.filter(info_resourceid=info_resourceid)
#        badges = Resource_Badge.objects.filter(info_resourceid=info_resourceid)

        serializer = self.serializer_class(item, context={'request': request}, many=False)
        return MyAPIResponse({'results': serializer.data})

    def post(self, request, format=None, **kwargs):
        info_resourceid = kwargs.get('info_resourceid')

        if not info_resourceid:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Info_ResourceID is required')

        try:
            resource = CiderInfrastructure.objects.get(info_resourceid=info_resourceid)
        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified Info_ResourceID not found')


        request_data = request.data
        roadmap_ids = request_data.get("roadmap_ids")
        badge_ids = request_data.get("badge_ids")

        try:
            roadmaps = Roadmap.objects.filter(roadmap_id__in=roadmap_ids)
        except Roadmap.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified roadmaps not found')

        try:
            badges = Badge.objects.filter(badge_id__in = badge_ids)
        except Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified badges not found')

        Resource_Roadmap.objects.filter(info_resourceid=info_resourceid).delete()
        Resource_Badge.objects.filter(info_resourceid=info_resourceid).delete()

        for roadmap in roadmaps:
            Resource_Roadmap(info_resourceid=info_resourceid, roadmap_id=roadmap).save()

        for badge in badges:
            # TODO validate if the badge is a part of enrolled roadmaps
            Resource_Badge(info_resourceid=info_resourceid, roadmap_id=roadmap, badge_id=badge).save()

        serializer = self.serializer_class(resource, context={'request': request}, many=False)
        return MyAPIResponse({'results': serializer.data})


class Badge_Task_v1(GenericAPIView):
    '''
    Retrieve tasks of a specific badge.
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = Badge_Task_Serializer

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



class Resource_Badge_Status_v1(GenericAPIView):
    '''
    Record Badge Status
    '''
    permission_classes = (AllowAny,)
    #permission_classes = [IsCoordinator | (IsAuthenticated & ReadOnly)]
    renderer_classes = (JSONRenderer,)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='badge_workflow_status',
                description='Filter by status',
                type=str,
                required=True,
                location=OpenApiParameter.PATH,
                enum=BadgeWorkflowStatus,
                default=BadgeWorkflowStatus.PLANNED
            )
        ]
    )
    def post(self, request, badge_workflow_status, *args, **kwargs):
        info_resourceid = kwargs.get('info_resourceid')
        roadmap_id = kwargs.get('roadmap_id')
        badge_id = kwargs.get('badge_id')

        if not info_resourceid or not roadmap_id or not badge_id or not badge_workflow_status:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Info_ResourceID, Roadmap ID, Badge ID and status are required')

        try:
            resource = CiderInfrastructure.objects.get(info_resourceid=info_resourceid)
            roadmap = Roadmap.objects.get(pk=roadmap_id)
            badge = Badge.objects.get(pk=badge_id)
        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified resource not found')
        except Roadmap.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified roadmap not found')
        except Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified badge not found')

        try:
            resource_badge = Resource_Badge.objects.get(info_resourceid=info_resourceid, roadmap=roadmap, badge=badge)
        except Resource_Badge.DoesNotExist:
            resource_badge = Resource_Badge(
                info_resourceid=resource,
                roadmap=roadmap,
                badge=badge
            )
            resource_badge.save()
            #raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified resource-badge relationship not found')


        # Update the status back to "PLANNED"
        workflow = Resource_Badge_Workflow(
            info_resourceid=info_resourceid,
            roadmap=roadmap,
            badge=badge,
            status=badge_workflow_status,
            status_updated_by=get_current_username(),
            status_updated_at=timezone.now()
        )
        workflow.save()

        return MyAPIResponse({'message': 'Badge marked as %s' % badge_workflow_status})

class Resource_Badge_Task_Status_v1(GenericAPIView):
    '''
    Record Badge Task Status
    '''
    permission_classes = (AllowAny,)
    #permission_classes = [IsCoordinator | (IsAuthenticated & ReadOnly)]
    renderer_classes = (JSONRenderer,)

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
        ]
    )
    def post(self, request, badge_task_workflow_status, *args, **kwargs):
        info_resourceid = kwargs.get('info_resourceid')
        roadmap_id = kwargs.get('roadmap_id')
        badge_id = kwargs.get('badge_id')
        task_id = kwargs.get('task_id')

        if not info_resourceid or not roadmap_id or not badge_id or not task_id or not badge_task_workflow_status:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Info_ResourceID, Roadmap ID, Badge ID, Task ID and status are required')

        try:
            resource = CiderInfrastructure.objects.get(info_resourceid=info_resourceid)
            roadmap = Roadmap.objects.get(pk=roadmap_id)
            badge = Badge.objects.get(pk=badge_id)
            task = Task.objects.get(pk=task_id)
        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified resource not found')
        except Roadmap.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified roadmap not found')
        except Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified badge not found')
        except Task.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified task not found')

        try:
            resource_badge = Resource_Badge.objects.get(info_resourceid=info_resourceid, roadmap=roadmap, badge=badge)
        except Resource_Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified resource-badge relationship not found')


        try:
            badge_task = Badge_Task.objects.get(badge=badge, task=task)
        except Badge_task.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified badge-task relationship not found')

        # Update the status back to "PLANNED"
        workflow = Resource_Badge_Task_Workflow(
            info_resourceid=info_resourceid,
            roadmap=roadmap,
            badge=badge,
            task=task,
            status=badge_task_workflow_status,
            status_updated_by=get_current_username(),
            status_updated_at=timezone.now()
        )
        workflow.save()

        return MyAPIResponse({'message': 'Badge task marked as %s' % badge_task_workflow_status})


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
