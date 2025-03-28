from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework import status
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



class Integration_Roadmap_v1(GenericAPIView):
    '''
        An ACCESS Generic Resource Detail
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = Integration_Roadmap_Serializer

    def get(self, request, format=None, **kwargs):
        many = self.kwargs.get('integration_roadmap_id') is None
        if self.kwargs.get('integration_roadmap_id'):
            try:
                item = Integration_Roadmap.objects.get(pk=self.kwargs['integration_roadmap_id'])
            except Integration_Roadmap.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified integration_roadmap_id not found')
        else:
            item = Integration_Roadmap.objects.all()

        serializer = self.serializer_class(item, context={'request': request}, many=many)
        return MyAPIResponse({'results': serializer.data})


class Integration_Badge_v1(GenericAPIView):
    '''
    Retrieve an Integration Badge by ID.
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = Integration_Badge_Full_Serializer

    def get(self, request, format=None, **kwargs):
        many = self.kwargs.get('integration_badge_id') is None
        if self.kwargs.get('integration_badge_id'):
            try:
                item = Integration_Badge.objects.get(pk=self.kwargs['integration_badge_id'])
            except Integration_Badge.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified integration_badge_id not found')
        else:
            item = Integration_Badge.objects.all()

        serializer = self.serializer_class(item, context={'request': request}, many=many)
        return MyAPIResponse({'results': serializer.data})


class Integration_Resource_List_v1(GenericAPIView):
    '''
    Retrieve all resources, including badges that are at least planned.
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderInfrastructure_Summary_Serializer
    # serializer_class = Integration_Resource_List_Serializer

    def get(self, request, format=None, **kwargs):
        badging_statuses = ('coming soon', 'friendly', 'pre-production', 'production', 'post-production')
        badging_types = ('Compute', 'Storage')

        resources = CiderInfrastructure.objects.filter(
            Q(cider_type__in=badging_types) & Q(latest_status__in=badging_statuses) & Q(
                project_affiliation__icontains='ACCESS'))

        serializer = self.serializer_class(resources, context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})


class Integration_Resource_v1(GenericAPIView):
    '''
    Retrieve details of a specific resource, including roadmaps and their badges. 
    It also includes the list of badge statuses of the badges that are at least planned.
    '''
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)
    serializer_class = Integration_Resource_Serializer

    def get(self, request, format=None, **kwargs):
        resource_id = kwargs.get('cider_resource_id')
        if not resource_id:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Resource ID is required')

        try:
            item = CiderInfrastructure.objects.get(pk=resource_id)
        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified resource not found')

        serializer = self.serializer_class(item, context={'request': request}, many=False)
        return MyAPIResponse({'results': serializer.data})

    def post(self, request, format=None, **kwargs):
        resource_id = kwargs.get('cider_resource_id')

        if not resource_id:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Resource ID is required')

        try:
            resource = CiderInfrastructure.objects.get(pk=resource_id)
        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified resource not found')


        request_data = request.data
        roadmap_ids = request_data.get("roadmap_ids")
        badge_ids = request_data.get("badge_ids")

        try:
            roadmaps = Integration_Roadmap.objects.filter(roadmap_id__in=roadmap_ids)
        except Integration_Roadmap.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified roadmaps not found')

        try:
            badges = Integration_Badge.objects.filter(badge_id__in = badge_ids)
        except Integration_Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified badges not found')

        Integration_Resource_Roadmap.objects.filter(resource_id=resource).delete()
        Integration_Resource_Badge.objects.filter(resource_id=resource).delete()

        for roadmap in roadmaps:
            Integration_Resource_Roadmap(roadmap_id=roadmap, resource_id=resource).save()

        for badge in badges:
            # TODO validate if the badge is a part of enrolled roadmaps
            Integration_Resource_Badge(badge_id=badge, resource_id=resource).save()

        serializer = self.serializer_class(resource, context={'request': request}, many=False)
        return MyAPIResponse({'results': serializer.data})


class Integration_Task_v1(GenericAPIView):
    '''
    Retrieve tasks of a specific badge.
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = Integration_Badge_Task_Serializer

    def get(self, request, *args, **kwargs):
        badge_id = kwargs.get('integration_badge_id')
        if not badge_id:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Badge ID is required')

        badge_tasks = Integration_Badge_Task.objects.filter(badge_id=badge_id).order_by('sequence_no')
        if badge_tasks.exists():
            serializer = self.serializer_class(badge_tasks, context={'request': request}, many=True)
            return MyAPIResponse({'results': serializer.data})
        else:
            # Return empty list if no tasks found, not an error
            return MyAPIResponse({'results': []})



class Integration_Resource_Badge_Status_v1(GenericAPIView):
    '''
    Mark a badge as task uncompleted.
    '''
    permission_classes = (AllowAny,)
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
        resource_id = kwargs.get('cider_resource_id')
        badge_id = kwargs.get('integration_badge_id')

        if not resource_id or not badge_id or not badge_workflow_status:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Resource ID, Badge ID and status are required')

        try:
            resource = CiderInfrastructure.objects.get(pk=resource_id)
            badge = Integration_Badge.objects.get(pk=badge_id)
        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified resource not found')
        except Integration_Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified badge not found')

        try:
            resource_badge = Integration_Resource_Badge.objects.get(resource_id=resource, badge_id=badge)
        except Integration_Resource_Badge.DoesNotExist:
            resource_badge = Integration_Resource_Badge(
                resource_id=resource,
                badge_id=badge
            )
            resource_badge.save()
            #raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified resource-badge relationship not found')


        # Update the status back to "PLANNED"
        workflow = Integration_Badge_Workflow(
            resource_id=resource,
            badge_id=badge,
            status=badge_workflow_status,
            status_updated_by=get_current_username(),
            status_updated_at=timezone.now()
        )
        workflow.save()

        return MyAPIResponse({'message': 'Badge marked as %s' % badge_workflow_status})

class Integration_Resource_Badge_Task_Status_v1(GenericAPIView):
    '''
    Mark a badge as task uncompleted.
    '''
    permission_classes = (AllowAny,)
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
        resource_id = kwargs.get('cider_resource_id')
        badge_id = kwargs.get('integration_badge_id')
        task_id = kwargs.get('integration_task_id')

        if not resource_id or not badge_id or not task_id or not badge_task_workflow_status:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Resource ID, Badge ID, Task ID and status are required')

        try:
            resource = CiderInfrastructure.objects.get(pk=resource_id)
            badge = Integration_Badge.objects.get(pk=badge_id)
            task = Integration_Task.objects.get(pk=task_id)
        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified resource not found')
        except Integration_Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified badge not found')

        try:
            resource_badge = Integration_Resource_Badge.objects.get(resource_id=resource, badge_id=badge)
        except Integration_Resource_Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified resource-badge relationship not found')


        try:
            resource_badge = Integration_Badge_Task.objects.get(badge_id=badge, task_id=task)
        except Integration_Resource_Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified badge-task relationship not found')

        # Update the status back to "PLANNED"
        workflow = Integration_Badge_Task_Workflow(
            resource_id=resource,
            badge_id=badge,
            task_id=task,
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
