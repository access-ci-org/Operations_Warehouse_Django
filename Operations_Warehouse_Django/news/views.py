from django.core.paginator import Paginator
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
        Single news item detail
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = News_v1_Detail_Serializer
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
        All news items optionally filtered by affiliation and publisher
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = News_v1_Detail_Serializer
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
        All outage type news items
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = Operations_Outages_v1_List_Expand_Serializer
    def get(self, request, format=None, **kwargs):
        items = News.objects.filter(NewsType__in=['Outage Full', 'Outage Partial', 'Reconfiguration'])
        serializer = Operations_Outages_v1_List_Expand_Serializer(items, context={'request': request})
        return MyAPIResponse({'results': serializer.data})

class News_v1_Current_Outages(GenericAPIView):
    '''
        All current outage type news items
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = News_v1_Outage_Serializer
    def get(self, request, format=None, **kwargs):
        now = timezone.now()
        items = News.objects.filter(Affiliation__exact=self.kwargs['affiliation'])\
                            .filter(NewsType__in=['Outage Full', 'Outage Partial', 'Reconfiguration'])
        items1 = items.filter(NewsStart__lte=now, NewsEnd__gte=now)
        items2 = items.filter(NewsStart__lte=now, NewsEnd__isnull=True)
        items = items1 | items2
        items = items.order_by('NewsStart')
        serializer = News_v1_Outage_Serializer(items, many=True, context={'request': request})
        return MyAPIResponse({'results': serializer.data})

class News_v1_Future_Outages(GenericAPIView):
    '''
        All future outage type news items
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = News_v1_Outage_Serializer
    def get(self, request, format=None, **kwargs):
        now = timezone.now()
        items = News.objects.filter(Affiliation__exact=self.kwargs['affiliation'])\
                            .filter(NewsType__in=['Outage Full', 'Outage Partial', 'Reconfiguration'])\
                            .filter(NewsStart__gte=now)\
                            .order_by('NewsStart')
        serializer = News_v1_Outage_Serializer(items, many=True, context={'request': request})
        return MyAPIResponse({'results': serializer.data})

class News_v1_Past_Outages(GenericAPIView):
    '''
        All past outage type news items, supports pagination
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = News_v1_Outage_Serializer
    def get(self, request, format=None, **kwargs):
        parm = request.GET.get('page')
        if parm:
            try:
                page = int(parm)
                if page == 0:
                    raise
            except:
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified page "{}" not valid'.format(parm))
        else:
            page = None
        try:
            parm = request.GET.get('results_per_page', 25)
            page_size = int(parm)
        except:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified page_size "{}" not valid'.format(parm))

        now = timezone.now()
        items = News.objects.filter(Affiliation__exact=self.kwargs['affiliation'])\
                            .filter(NewsType__in=['Outage Full', 'Outage Partial', 'Reconfiguration'])\
                            .filter(NewsStart__lte=now)\
                            .exclude(NewsEnd__isnull=False, NewsEnd__gt=now)\
                            .order_by('-NewsStart')
        response_obj = {}
        if page:
            paginator = Paginator(items, page_size)
            final_items = paginator.page(page)
            response_obj['page'] = page
            response_obj['total_pages'] = paginator.num_pages
        else:
            final_items = items

        serializer = News_v1_Outage_Serializer(final_items, many=True, context={'request': request})
        response_obj['results'] = serializer.data
        return MyAPIResponse(response_obj)

class News_v1_All_Outages(GenericAPIView):
    '''
        All future outage type news items, supports pagination
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = News_v1_Outage_Serializer
    def get(self, request, format=None, **kwargs):
        now = timezone.now()
        items = News.objects.filter(Affiliation__exact=self.kwargs['affiliation'])\
                            .filter(NewsType__in=['Outage Full', 'Outage Partial', 'Reconfiguration'])
        serializer = News_v1_Outage_Serializer(items, many=True, context={'request': request})
        return MyAPIResponse({'results': serializer.data})
