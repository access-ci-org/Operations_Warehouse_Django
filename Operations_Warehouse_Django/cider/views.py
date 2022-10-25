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
        objects = CiderInfrastructure_Active(affiliation='XSEDE', allocated=True, type='ALL', result='OBJECTS')
        serializer = CiderInfrastructure_Serializer(objects, many=True)
        return MyAPIResponse({'results': serializer.data})
