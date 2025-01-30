from django.db.models import Q
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from django.db import transaction
from django.utils import timezone

from integration_badges.models import *
# from integration_badges.filters import *
from integration_badges.serializers import *

from warehouse_tools.exceptions import MyAPIException
from warehouse_tools.responses import MyAPIResponse



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
    serializer_class = Integration_Resource_List_Serializer

    def get(self, request, format=None, **kwargs):
        # Filter out only Compute and Storage resources
        item = CiderInfrastructure.objects.filter(cider_type__in=['Compute', 'Storage'])

        serializer = self.serializer_class(item, context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})


class Integration_Resource_v1(GenericAPIView):
    '''
    Retrieve details of a specific resource, including roadmaps and their badges. 
    It also includes the list of badge states of the badges that are at least planned.
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
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


class Integration_Resource_Badge_Plan_v1(GenericAPIView):
    '''
    Plan or update a badge for a resource.
    '''
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)
    serializer_class = Integration_Resource_Badge_Plan_Serializer

    def post(self, request, *args, **kwargs):
        resource_id = kwargs.get('cider_resource_id')
        badge_id = kwargs.get('integration_badge_id')

        if not resource_id or not badge_id:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Resource ID and Badge ID are required') 

        try:
            resource = CiderInfrastructure.objects.get(pk=resource_id)
            badge = Integration_Badge.objects.get(pk=badge_id)
        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified resource not found')
        except Integration_Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified badge not found')

       # Check if the resource_badge already exists
        try:
            resource_badge = Integration_Resource_Badge.objects.get(resource_id=resource, badge_id=badge)
            serializer = self.serializer_class(resource_badge, data=request.data, partial=True)
        except Integration_Resource_Badge.DoesNotExist:
            # if the resource_badge does not exist, create a new one
            serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            try:
                with transaction.atomic():
                    resource_badge = serializer.save(resource=resource, badge=badge)
                    status_code = status.HTTP_201_CREATED if 'resource_badge' not in locals() else status.HTTP_200_OK
                    return MyAPIResponse({"resource_badge_id": resource_badge.id}, code=status_code)
            except Exception as e:
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail="Error saving the resource_badge: " + str(e))
        else:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail="Invalid data: " + str(serializer.errors))


class Integration_Resource_Badge_Unplan_v1(GenericAPIView):
    '''
    Delete a resource-badge object.
    '''
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)
    
    def post(self, request, *args, **kwargs):
        resource_id = kwargs.get('cider_resource_id')
        badge_id = kwargs.get('integration_badge_id')

        if not resource_id or not badge_id:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Resource ID and Badge ID are required')

        try:
            resource = CiderInfrastructure.objects.get(pk=resource_id)
            badge = Integration_Badge.objects.get(pk=badge_id)
        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified resource not found')
        except Integration_Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified badge not found')

        try:
            resource_badge = Integration_Resource_Badge.objects.get(resource_id=resource, badge_id=badge)
            resource_badge.delete()
            return MyAPIResponse({"detail": "Resource badge deleted successfully"}, code=status.HTTP_204_NO_CONTENT)
        except Integration_Resource_Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Resource badge not found')


class Integration_Resource_Badge_Status_v1(GenericAPIView):
    '''
    Retrieve badge status of a resource.
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = Integration_Resource_Badge_Status_Serializer

    def get(self, request, format=None, **kwargs):
        resource_id = kwargs.get('cider_resource_id')
        if not resource_id:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Resource ID is required')

        try:
            item = CiderInfrastructure.objects.get(pk=resource_id)
        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified resource not found')

        serializer = self.serializer_class(item, context={'request': request}, many=False)
        return MyAPIResponse({'results': serializer.data})


class Integration_Resource_Badge_Task_Completed_v1(GenericAPIView):
    '''
    Mark a badge as task completed.
    '''
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)

    def post(self, request, *args, **kwargs):
        resource_id = kwargs.get('cider_resource_id')
        badge_id = kwargs.get('integration_badge_id')

        if not resource_id or not badge_id:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Resource ID and Badge ID are required') 

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
            # if the resource_badge does not exist, throw an error
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified resource-badge relationship not found')
        
        # Update the state to "TASK_COMPLETED"
        workflow = Integration_Badge_Workflow(
            resource_id=resource,
            badge_id=badge,
            state=BADGE_WORKFLOW_STATE["TASK_COMPLETED"],
            state_updated_by=get_current_username(),
            state_updated_at=timezone.now()
        )
        workflow.save()

        return MyAPIResponse({'message': 'Task marked as completed'})


class Integration_Resource_Badge_Task_Uncompleted_v1(GenericAPIView):
    '''
    Mark a badge as task uncompleted.
    '''
    permission_classes = (AllowAny,)
    renderer_classes = (JSONRenderer,)

    def post(self, request, *args, **kwargs):
        resource_id = kwargs.get('cider_resource_id')
        badge_id = kwargs.get('integration_badge_id')

        if not resource_id or not badge_id:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Resource ID and Badge ID are required')

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
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified resource-badge relationship not found')

        # Update the state back to "PLANNED"
        workflow = Integration_Badge_Workflow(
            resource_id=resource,
            badge_id=badge,
            state=BADGE_WORKFLOW_STATE["PLANNED"],
            state_updated_by=get_current_username(),
            state_updated_at=timezone.now()
        )
        workflow.save()

        return MyAPIResponse({'message': 'Task marked as uncompleted (state as planned)'})
