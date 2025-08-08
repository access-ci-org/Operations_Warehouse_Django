from django.shortcuts import render

from drf_spectacular.utils import OpenApiParameter, extend_schema
from itertools import chain
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework import status
from rest_framework.generics import GenericAPIView

from cider.models import *
from cider.filters import *
from .serializers import *

from warehouse_tools.exceptions import MyAPIException
from warehouse_tools.responses import MyAPIResponse, CustomPagePagination

# Create your views here.

class CiderInfrastructure_v1_SGCIActiveList_100(GenericAPIView):
    '''
    SGCI Resource Descriptions from CiDeR about ACTIVE ACCESS and TACC resources, meaning:
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)
    def get(self, request, format=None):
        import pdb
        pdb.set_trace()
        objects_ACCESS = CiderInfrastructure_Active_Filter(affiliation='ACCESS',result='OBJECTS')
        objects_TACC = CiderInfrastructure_Active_Filter(affiliation='TACC', result='OBJECTS')
        serializer = SGCI_Resource_100_Serializer(objects_ACCESS | objects_TACC, many=True)
        return MyAPIResponse({'results': serializer.data}, template_name='sgci_resources.html')