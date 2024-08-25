from django.db.models import Q
from django.shortcuts import render
from drf_spectacular.utils import OpenApiParameter, extend_schema
from itertools import chain
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView

from .models import *
from .filters import *
from .serializers import *

from warehouse_tools.exceptions import MyAPIException
from warehouse_tools.responses import MyAPIResponse, CustomPagePagination
# Create your views here.

class CiderInfrastructure_v1_ACCESSActiveList(GenericAPIView):
    '''
        All ACCESS Active Allocated Compute and Storage Resources
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderInfrastructure_Summary_Serializer
    def get(self, request, format=None, **kwargs):
        objects = CiderInfrastructure_ActiveAllocated_Filter(affiliation='ACCESS', result='OBJECTS')
        serializer = CiderInfrastructure_Summary_Serializer(objects, context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})

class CiderInfrastructure_v2_ACCESSActiveList(GenericAPIView):
    '''
        All ACCESS Active Allocated Compute and Storage Resources and Central Online Services Resources
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderInfrastructure_Summary_Serializer
    def get(self, request, format=None, **kwargs):
        objects1 = CiderInfrastructure_ActiveAllocated_Filter(affiliation='ACCESS', result='OBJECTS')
        objects2 = CiderInfrastructure_Active_Filter(affiliation='ACCESS', result='OBJECTS', type='Online Service')
        serializer = CiderInfrastructure_Summary_Serializer(chain(objects1, objects2), context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})

class CiderInfrastructure_v2_ACCESSAllList(GenericAPIView):
    '''
        All ACCESS Active and Inactive Compute and Storage Resources and Central Online Services Resources
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderInfrastructure_Summary_Serializer
    def get(self, request, format=None, **kwargs):
        objects1 = CiderInfrastructure_All_Filter(affiliation='ACCESS', result='OBJECTS', type='Compute')
        objects2 = CiderInfrastructure_All_Filter(affiliation='ACCESS', result='OBJECTS', type='Storage')
        serializer = CiderInfrastructure_Summary_Serializer(chain(objects1, objects2), context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})
    
class CiderInfrastructure_v1_ACCESSAllocatedList(GenericAPIView):
    '''
        All ACCESS Allocated Resources
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderInfrastructure_Summary_Serializer
    def get(self, request, format=None, **kwargs):
        objects = CiderInfrastructure_ActiveAllocated_Filter(affiliation='ACCESS', result='OBJECTS')
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
        objects = CiderInfrastructure_Active_Filter(affiliation='ACCESS', result='OBJECTS', type='Online Service')
        serializer = CiderInfrastructure_Summary_v2_Serializer(objects, context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})

class CiderInfrastructure_v1_ACCESSScienceGatewaysList(GenericAPIView):
    '''
        All ACCESS Science Gateways
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderInfrastructure_Summary_Serializer
    @extend_schema(parameters=[
            OpenApiParameter('search', str, OpenApiParameter.QUERY),
            OpenApiParameter('page', int, OpenApiParameter.QUERY),
            OpenApiParameter('page_size', int, OpenApiParameter.QUERY)
        ])
    def get(self, request, format=None, **kwargs):
        arg_string = request.query_params.get('search')
        if arg_string:
            want_string = arg_string.lower()
        else:
            want_string = None
        try:
            page = request.GET.get('page')
            if page:
                page = int(page)
                if page == 0:
                    raise
        except:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Pagination page "{}" is not valid'.format(page))

        objects = CiderInfrastructure_Active_Filter(affiliation='ACCESS', result='OBJECTS', type='Science Gateway', search=want_string)
        
        if not page:
            serializer = CiderInfrastructure_Summary_v2_Gateway_Serializer(objects, context={'request': request}, many=True)
            return MyAPIResponse({'results': serializer.data})

        objects = objects.order_by('resource_descriptive_name')
        paginator = CustomPagePagination()
        query_page = paginator.paginate_queryset(objects, request, view=self)
        serializer = CiderInfrastructure_Summary_v2_Gateway_Serializer(query_page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data, request)

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
                item = CiderInfrastructure.objects.get(info_resourceid=self.kwargs['info_resourceid'])
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
                if item.cider_type != 'Compute':
                    raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified cider_resource_id is of a different type')
#                if item.parent_resource: # Serializer wants the parent, but will serialize both
#                    item =  CiderInfrastructure.objects.get(pk=item.parent_resource)
            except CiderInfrastructure.DoesNotExist:
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified cider_resource_id not found')
        else:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Missing selection parameter')
        serializer = CiderInfrastructure_Compute_Detail_Serializer(item, context={'request': request})
        return MyAPIResponse({'results': serializer.data})
