from django.db.models import Q
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView

from cider.models import *
from cider.filters import *
from cider.serializers import *

from warehouse_tools.exceptions import MyAPIException
from warehouse_tools.responses import MyAPIResponse
# Create your views here.

class CiderInfrastructure_v1_ACCESSActiveList(GenericAPIView):
    '''
        All ACCESS Active Resources
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderInfrastructure_Summary_Serializer
    def get(self, request, format=None, **kwargs):
        objects = CiderInfrastructure_AllocatedResources(affiliation='ACCESS', result='OBJECTS')
        serializer = CiderInfrastructure_Summary_Serializer(objects, context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})

class CiderInfrastructure_v1_ACCESSAllocatedList(GenericAPIView):
    '''
        All ACCESS Allocated Resources
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderInfrastructure_Summary_Serializer
    def get(self, request, format=None, **kwargs):
        objects = CiderInfrastructure_AllocatedResources(affiliation='ACCESS', result='OBJECTS')
        serializer = CiderInfrastructure_Summary_v2_Serializer(objects, context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})

class CiderInfrastructure_v1_ACCESSOnlineServicesList(GenericAPIView):
    '''
        All ACCESS Online Services
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderInfrastructure_Summary_Serializer
    def get(self, request, format=None, **kwargs):
        objects = CiderInfrastructure_ActiveOnlineServices(affiliation='ACCESS', result='OBJECTS')
        serializer = CiderInfrastructure_Summary_v2_Serializer(objects, context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})

class CiderInfrastructure_v1_Detail(GenericAPIView):
    '''
        An ACCESS Generic Resource Detail
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderInfrastructure_Detail_Serializer
    def get(self, request, format=None, **kwargs):
        # We need the base resource to pass to the serializer
        if self.kwargs.get('cider_resource_id'):        # Whether base or sub resource, grab the other one also
            try:
                item = CiderInfrastructure.objects.get(pk=self.kwargs['cider_resource_id'])
                if item.parent_resource: # Serializer wants the parent, but will serialize both
                    item =  CiderInfrastructure.objects.get(pk=item.parent_resource)
            except CiderInfrastructure.DoesNotExist:
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified cider_resource_id not found')
        elif self.kwargs.get('info_resourceid'):
            try:
                item = CiderInfrastructure.objects.get(info_resourceid=self.kwargs['info_resourceid'], cider_type='resource')
            except (CiderInfrastructure.DoesNotExist, CiderInfrastructure.MultipleObjectsReturned):
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified info_resourceid did not match a single resource')
        else:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Missing selection parameter')
        serializer = CiderInfrastructure_Detail_Serializer(item, context={'request': request})
        return MyAPIResponse({'results': serializer.data})

class CiderInfrastructure_v1_Compute_Detail(GenericAPIView):
    '''
        An ACCESS Compute Resource Detail
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderInfrastructure_Detail_Serializer
    def get(self, request, format=None, **kwargs):
        # We need the base resource to pass to the serializer
        if self.kwargs.get('cider_resource_id'):        # Whether base or sub resource, grab the other one also
            try:
                item = CiderInfrastructure.objects.get(pk=self.kwargs['cider_resource_id'])
                if item.cider_type != 'compute':
                    raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified cider_resource_id is of a different type')
#                if item.parent_resource: # Serializer wants the parent, but will serialize both
#                    item =  CiderInfrastructure.objects.get(pk=item.parent_resource)
            except CiderInfrastructure.DoesNotExist:
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified cider_resource_id not found')
        else:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Missing selection parameter')
        serializer = CiderInfrastructure_Compute_Detail_Serializer(item, context={'request': request})
        return MyAPIResponse({'results': serializer.data})
