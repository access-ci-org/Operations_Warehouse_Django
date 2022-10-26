from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework import status

from cider.models import *
from cider.filters import *
from cider.serializers import *

from warehouse_tools.exceptions import MyAPIException
from warehouse_tools.responses import MyAPIResponse
# Create your views here.

class CiderInfrastructure_v1_ACCESSActiveList(APIView):
    '''
        All ACCESS Active Resources
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    def get(self, request, format=None, **kwargs):
        objects = CiderInfrastructure_Active(affiliation='XSEDE', allocated=True, type='BASE', result='OBJECTS')
        serializer = CiderInfrastructure_Summary_Serializer(objects, context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})

class CiderInfrastructure_v1_Detail(APIView):
    '''
        An ACCESS Resource Detail
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    def get(self, request, format=None, **kwargs):
        if self.kwargs.get('cider_resource_id'):
            try:
                objects = [CiderInfrastructure.objects.get(pk=self.kwargs['cider_resource_id'])]
            except CiderInfrastructure.DoesNotExist:
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified cider_resource_id not found')
        elif self.kwargs.get('info_resourceid'):
            try:
                objects = CiderInfrastructure.objects.filter(info_resourceid__exact=self.kwargs['info_resourceid'])
            except CiderInfrastructure.DoesNotExist:
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified info_resourceid not found')
        else:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Missing selection parameter')
        serializer = CiderInfrastructure_Detail_Serializer(objects, context={'request': request}, many=True)
        return MyAPIResponse({'result_set': serializer.data})
