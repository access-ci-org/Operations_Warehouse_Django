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
