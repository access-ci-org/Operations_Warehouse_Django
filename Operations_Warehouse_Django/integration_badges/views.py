from django.db.models import Q
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView

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
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified integration_roadmap_id not found')
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
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified integration_badge_id not found')
        else:
            item = Integration_Badge.objects.all()

        serializer = self.serializer_class(item, context={'request': request}, many=many)
        return MyAPIResponse({'results': serializer.data})

class Integration_Resource_List_v1(GenericAPIView):
    '''
    Retrieve all resources, including ids of the badges of each resource.
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = Integration_Resource_List_Serializer

    def get(self, request, format=None, **kwargs):
        item = CiderInfrastructure.objects.all()

        serializer = self.serializer_class(item, context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})

class Integration_Resource_v1(GenericAPIView):
    '''
    Retrieve details of a specific resource, including different roadmaps and badges.
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
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified resource not found')

        serializer = self.serializer_class(item, context={'request': request}, many=False)
        return MyAPIResponse({'results': serializer.data})

class Integration_Task_v1(GenericAPIView):
    '''
    Retrieve tasks of a certain badge.
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = Integration_Badge_Task_Serializer

    def get(self, request, *args, **kwargs):
        badge_id = kwargs.get('integration_badge_id')
        if not badge_id:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Badge ID is required')

        try:
            badge_tasks = Integration_Badge_Task.objects.filter(badge_id=badge_id)
            if not badge_tasks:
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail="Specified badge has no associated tasks.")
        except Integration_Badge_Task.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified badge tasks not found')

        serializer = self.serializer_class(badge_tasks, context={'request': request}, many=True)
        return Response(serializer.data)