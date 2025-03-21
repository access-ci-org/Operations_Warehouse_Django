from django.db.models import Subquery
from django.shortcuts import render
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer

from warehouse_tools.exceptions import MyAPIException
from warehouse_tools.responses import MyAPIResponse, CustomPagePagination

from .models import *
from .serializers import *

outage_types = ['Degraded', 'Outage Full', 'Outage Partial', 'Reconfiguration']

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

class News_v1_List(ListAPIView):
    '''
        All news items optionally filtered by affiliation and publisher
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = News_v1_Outage_Serializer
    @extend_schema(parameters=[
            OpenApiParameter('affiliation', str, OpenApiParameter.QUERY),
            OpenApiParameter('publisher', str, OpenApiParameter.QUERY),
            OpenApiParameter('page', int, OpenApiParameter.QUERY),
            OpenApiParameter('page_size', int, OpenApiParameter.QUERY)
        ])
    def get(self, request, format=None, **kwargs):
        if request.GET.get('affiliation'):
            queryset = News.objects.filter(Affiliation__exact=request.GET.get('affiliation'))
        else:
            queryset = None
        if request.GET.get('publisher'):
            if queryset:
                queryset = queryset.filter(Publisher__exact=request.GET.get('publisher'))
            else:
                queryset = News.objects.filter(Publisher__exact=request.GET.get('publisher'))
        if queryset is None:
            queryset = News.objects.all()
        queryset = queryset.order_by('-NewsStart')

        try:
            page = request.GET.get('page')
            if page:
                page = int(page)
                if page == 0:
                    raise
        except:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Pagination page "{}" is not valid'.format(page))

        if not page:
            serializer = News_v1_Outage_Serializer(queryset, many=True, context={'request': request})
            return MyAPIResponse({'results': serializer.data})

#        try:
#            page_size = request.GET.get('page_size')
#            if page_size:
#                page_size = int(page_size)
#        except:
#            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Pagination page_size "{}" is not valid'.format(page_size))

        paginator = CustomPagePagination()
        query_page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = News_v1_Outage_Serializer(query_page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data, request)

class Operations_Outages_v1(GenericAPIView):
    '''
        All outage type news items
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = Operations_Outages_v1_List_Expand_Serializer
    def get(self, request, format=None, **kwargs):
        items = News.objects.filter(NewsType__in=outage_types)
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
                            .filter(NewsType__in=outage_types)
        items1 = items.filter(NewsStart__lte=now, NewsEnd__gte=now)
        items2 = items.filter(NewsStart__lte=now, NewsEnd__isnull=True)
        items = items1 | items2
        items = items.order_by('NewsStart')
        serializer = News_v1_Outage_Serializer(items, many=True, context={'request': request})
        return MyAPIResponse({'results': serializer.data})

class News_v2_Current_Outages(GenericAPIView):
    '''
        Current outage type news items for a selected group
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = News_v1_Outage_Serializer
    def get(self, request, format=None, **kwargs):
        resource_ids = None
        if self.kwargs.get('info_groupid'):
            try:
                group = CiderGroups.objects.get(info_groupid=self.kwargs['info_groupid'])
            except (CiderGroups.DoesNotExist, CiderGroups.MultipleObjectsReturned):
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified info_groupid not found')
            resource_ids = group.info_resourceids
        now = timezone.now()
        items = News.objects.filter(NewsType__in=outage_types)
        if self.kwargs.get('affiliation'):
            items = items.objects.filter(Affiliation__exact=self.kwargs['affiliation'])
        if resource_ids:
            related_to = News_Associations.objects.filter(AssociatedType='Resource', AssociatedID__in=resource_ids)
            items = items.filter(URN__in=Subquery(related_to.values('NewsItem')))
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
                            .filter(NewsType__in=outage_types)\
                            .filter(NewsStart__gte=now)\
                            .order_by('NewsStart')
        serializer = News_v1_Outage_Serializer(items, many=True, context={'request': request})
        return MyAPIResponse({'results': serializer.data})

class News_v2_Future_Outages(GenericAPIView):
    '''
        All future outage type news items for a selected group
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = News_v1_Outage_Serializer
    def get(self, request, format=None, **kwargs):
        resource_ids = None
        if self.kwargs.get('info_groupid'):
            try:
                group = CiderGroups.objects.get(info_groupid=self.kwargs['info_groupid'])
            except (CiderGroups.DoesNotExist, CiderGroups.MultipleObjectsReturned):
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified info_groupid not found')
            resource_ids = group.info_resourceids
        now = timezone.now()
        items = News.objects.filter(NewsType__in=outage_types)\
                            .filter(NewsStart__gte=now)\
                            .order_by('NewsStart')
        if self.kwargs.get('affiliation'):
            items = items.objects.filter(Affiliation__exact=self.kwargs['affiliation'])
        if resource_ids:
            related_resources = News_Associations.objects.filter(AssociatedType='Resource', AssociatedID__in=resource_ids)
            items = items.filter(URN__in=Subquery(related_resources.values('NewsItem_id')))
        serializer = News_v1_Outage_Serializer(items, many=True, context={'request': request})
        return MyAPIResponse({'results': serializer.data})

class News_v2_Filter_Outages(GenericAPIView):
    '''
        All outage type news items for a selected group with filtering parameters
        
        - Optionally filter within window_start_date and window_end_date 
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = News_v1_Outage_Serializer
    @extend_schema(parameters=[
            OpenApiParameter('window_start_date', OpenApiTypes.DATE, OpenApiParameter.QUERY),
            OpenApiParameter('window_end_date', OpenApiTypes.DATE, OpenApiParameter.QUERY)
        ])
    def get(self, request, format=None, **kwargs):
        resource_ids = None
        if self.kwargs.get('info_groupid'):
            try:
                group = CiderGroups.objects.get(info_groupid=self.kwargs['info_groupid'])
            except (CiderGroups.DoesNotExist, CiderGroups.MultipleObjectsReturned):
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified info_groupid not found')
            resource_ids = group.info_resourceids
        items = News.objects.filter(NewsType__in=outage_types)\
                            .order_by('NewsStart')
        # If start_date specified, include no end_date or NewsEnd equal to or after start_date
        window_start = request.GET.get('window_start_date')
        if window_start:
            items1 = items.filter(NewsEnd__isnull=True)
            items2 = items.filter(NewsEnd__gte=window_start)
            items = items1 | items2
        # If end_date specified, include events with a NewsStart equal to or before end_date
        window_end = request.GET.get('window_end_date')
        if window_end:
            items = items.filter(NewsStart__lte=window_end)
        now = timezone.now()
        if self.kwargs.get('affiliation'):
            items = items.objects.filter(Affiliation__exact=self.kwargs['affiliation'])
        if resource_ids:
            related_resources = News_Associations.objects.filter(AssociatedType='Resource', AssociatedID__in=resource_ids)
            items = items.filter(URN__in=Subquery(related_resources.values('NewsItem_id')))
        serializer = News_v1_Outage_Serializer(items, many=True, context={'request': request})
        return MyAPIResponse({'results': serializer.data})

class News_v1_Past_Outages(ListAPIView):
    '''
        All past outage type news items, supports pagination
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = News_v1_Outage_Serializer
    pagination_class = CustomPagePagination
    @extend_schema(parameters=[
            OpenApiParameter('page', int, OpenApiParameter.QUERY),
            OpenApiParameter('page_size', int, OpenApiParameter.QUERY)
        ])
    def get(self, request, format=None, **kwargs):
        now = timezone.now()
        queryset = News.objects.filter(Affiliation__exact=self.kwargs['affiliation'])\
                            .filter(NewsType__in=outage_types)\
                            .filter(NewsStart__lte=now)\
                            .exclude(NewsEnd__isnull=False, NewsEnd__gt=now)\
                            .order_by('-NewsStart')

        try:
            page = request.GET.get('page')
            if page:
                page = int(page)
                if page == 0:
                    raise
        except:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Pagination page "{}" is not valid'.format(page))

        if not page:
            serializer = News_v1_Outage_Serializer(queryset, many=True, context={'request': request})
            return MyAPIResponse({'results': serializer.data})

#        try:
#            page_size = request.GET.get('page_size')
#            if page_size:
#                page_size = int(page_size)
#        except:
#            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Pagination page_size "{}" is not valid'.format(page_size))

        paginator = CustomPagePagination()
        query_page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = News_v1_Outage_Serializer(query_page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data, request)

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
                            .filter(NewsType__in=outage_types)
        serializer = News_v1_Outage_Serializer(items, many=True, context={'request': request})
        return MyAPIResponse({'results': serializer.data})
