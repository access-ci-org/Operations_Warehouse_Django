from django.shortcuts import render
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer

from news.models import *
from news.serializers import *

from warehouse_tools.exceptions import MyAPIException
from warehouse_tools.responses import MyAPIResponse
# Create your views here.

class News_v1_Detail(GenericAPIView):
    '''
        News Detail
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_classes = (News_v1_Detail_Serializer,)
    def get(self, request, format=None, **kwargs):
        # We need the base resource to pass to the serializer
        if self.kwargs.get('ID'):
            try:
                item = News.objects.get(pk=self.kwargs['ID'])
            except News.DoesNotExist:
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified News ID not found')
        else:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Missing selection parameter')
        serializer = News_v1_Detail_Serializer(item, context={'request': request})
        return MyAPIResponse({'results': serializer.data})

class News_v1_List(GenericAPIView):
    '''
        An Operations News List
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_classes = (News_v1_Detail_Serializer,)
    def get(self, request, format=None, **kwargs):
        # We need the base resource to pass to the serializer
        if self.kwargs.get('affiliation'):
            items = News.objects.filter(Affiliation__exact=self.kwargs['affiliation'])
        elif self.kwargs.get('publisher'):
            items = News.objects.filter(Publisher__exact=self.kwargs['publisher'])
        else:
            items = News.objects.all()
        serializer = News_v1_Detail_Serializer(items, context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})

class Operations_Outages_v1(GenericAPIView):
    '''
        Operations Outages
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_classes = (Operations_Outages_v1_List_Expand_Serializer,)
    def get(self, request, format=None, **kwargs):
        items = News.objects.filter(NewsType__in=['Outage Full', 'Outage Partial', 'Reconfiguration'])
        serializer = Operations_Outages_v1_List_Expand_Serializer(items, context={'request': request})
        return MyAPIResponse({'results': serializer.data})


class News_v1_Current_Outages(GenericAPIView):
    '''
        Current Operations News List
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_classes = (News_v1_Outage_Serializer,)
    def get(self, request, format=None, **kwargs):
        now = timezone.now()
        items = News.objects.filter(Affiliation__exact=self.kwargs['affiliation'])\
                            .filter(NewsType__in=['Outage Full', 'Outage Partial', 'Reconfiguration'])
        items1 = items.filter(NewsStart__lte=now, NewsEnd__gte=now)
        items2 = items.filter(NewsStart__lte=now, NewsEnd__isnull=True)
        items = items1 | items2
        serializer = News_v1_Outage_Serializer(items, many=True, context={'request': request})
        return MyAPIResponse({'results': serializer.data})

class News_v1_Future_Outages(GenericAPIView):
    '''
        Current Operations News List
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_classes = (News_v1_Outage_Serializer,)
    def get(self, request, format=None, **kwargs):
        now = timezone.now()
        items = News.objects.filter(Affiliation__exact=self.kwargs['affiliation'])\
                            .filter(NewsType__in=['Outage Full', 'Outage Partial', 'Reconfiguration'])\
                            .filter(NewsStart__gte=now)
        serializer = News_v1_Outage_Serializer(items, many=True, context={'request': request})
        return MyAPIResponse({'results': serializer.data})

class News_v1_All_Outages(GenericAPIView):
    '''
        Current Operations News List
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_classes = (News_v1_Outage_Serializer,)
    def get(self, request, format=None, **kwargs):
        now = timezone.now()
        items = News.objects.filter(Affiliation__exact=self.kwargs['affiliation'])\
                            .filter(NewsType__in=['Outage Full', 'Outage Partial', 'Reconfiguration'])
        serializer = News_v1_Outage_Serializer(items, many=True, context={'request': request})
        return MyAPIResponse({'results': serializer.data})
