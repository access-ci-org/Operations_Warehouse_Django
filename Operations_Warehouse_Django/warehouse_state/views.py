# Create your views here.
from django.utils.encoding import uri_to_iri
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework import status

from .models import *
from .serializers import *

from warehouse_tools.exceptions import MyAPIException
from warehouse_tools.responses import MyAPIResponse

# Create your views here.
class ProcessingStatus_DbList(ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,TemplateHTMLRenderer,)
    serializer_class = ProcessingStatus_DetailURL_DbSerializer
    @extend_schema(parameters=[
            OpenApiParameter('about', str, OpenApiParameter.QUERY),
            OpenApiParameter('topic', str, OpenApiParameter.QUERY),
            OpenApiParameter('page', int, OpenApiParameter.QUERY),
            OpenApiParameter('page_size', int, OpenApiParameter.QUERY),
            OpenApiParameter('sort', str, OpenApiParameter.QUERY),
        ])
    def get(self, request, format=None, **kwargs):
        if 'about' in self.kwargs:
            try:
                objects = ProcessingStatus.objects.filter(About__exact=uri_to_iri(self.kwargs['about']))
            except ProcessingStatus.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified about not found')
        elif 'topic' in self.kwargs:
            try:
                objects = ProcessingStatus.objects.filter(Topic__exact=uri_to_iri(self.kwargs['topic']))
            except ProcessingStatus.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified topic not found')
        else:
            try:
                objects = ProcessingStatus.objects.all()
            except ProcessingStatus.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='No objects found')
        try:
            sort_by = request.GET.get('sort')
            objects_sorted = objects.order_by(sort_by)
        except:
            objects_sorted = objects
        serializer = ProcessingStatus_DetailURL_DbSerializer(objects_sorted, context={'request': request}, many=True)
        return MyAPIResponse({'record_list': serializer.data}, template_name='warehouse_state/list.html')

class ProcessingStatus_LatestList(ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,TemplateHTMLRenderer,)
    serializer_class = ProcessingStatus_DbSerializer
    @extend_schema(parameters=[
            OpenApiParameter('about', str, OpenApiParameter.QUERY),
            OpenApiParameter('topic', str, OpenApiParameter.QUERY),
            OpenApiParameter('page', int, OpenApiParameter.QUERY),
            OpenApiParameter('page_size', int, OpenApiParameter.QUERY)
        ])
    def get(self, request, format=None, **kwargs):
        if 'about' in self.kwargs:
            try:
                object = ProcessingStatus.objects.filter(About__exact=uri_to_iri(self.kwargs['about'])).latest('ProcessingStart')
            except ProcessingStatus.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified about not found')
        elif 'topic' in self.kwargs:
            try:
                object = ProcessingStatus.objects.filter(Topic__exact=uri_to_iri(self.kwargs['topic'])).latest('ProcessingStart')
            except ProcessingStatus.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified topic not found')
        else:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
        serializer = ProcessingStatus_DbSerializer(object)
        return MyAPIResponse({'record_list': [serializer.data]}, template_name='warehouse_state/detail.html')

class ProcessingStatus_Detail(GenericAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,TemplateHTMLRenderer,)
    serializer_class = ProcessingStatus_DetailURL_DbSerializer
    @extend_schema(parameters=[
            OpenApiParameter('id', str, OpenApiParameter.QUERY),
        ])
    def get(self, request, format=None, **kwargs):
        if 'id' in self.kwargs:
            try: #uri_to_iri(
                object = ProcessingStatus.objects.get(pk=self.kwargs['id'])
            except ProcessingStatus.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified id not found')
        else:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
        if request.accepted_renderer.format == 'html':
            return MyAPIResponse({'record_list': [object]}, template_name='warehouse_state/detail.html')
        serializer = ProcessingStatus_DbSerializer(object)
        return MyAPIResponse({'record_list': [serializer.data]})

class PublisherInfo_DbList(ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,TemplateHTMLRenderer,)
    serializer_class = PublisherInfo_DetailURL_DbSerializer
    @extend_schema(parameters=[
            OpenApiParameter('resourceid', str, OpenApiParameter.QUERY),
        ])
    def get(self, request, format=None, **kwargs):
        if 'resourceid' in self.kwargs:
            try:
                objects = PublisherInfo.objects.filter(ResourceID__exact=uri_to_iri(self.kwargs['resourceid']))
            except PublisherInfo.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified ResourceID not found')
        else:
            try:
                objects = PublisherInfo.objects.all()
            except PublisherInfo.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='No objects found')
        try:
            sort_by = request.GET.get('sort')
            objects_sorted = objects.order_by(sort_by)
        except:
            objects_sorted = objects

        serializer = PublisherInfo_DetailURL_DbSerializer(objects_sorted, context={'request': request}, many=True)
        return MyAPIResponse({'record_list': serializer.data}, template_name='warehouse_state/publisher_list.html')

class PublisherInfo_Detail(GenericAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,TemplateHTMLRenderer,)
    serializer_class = PublisherInfo_DetailURL_DbSerializer
    def get(self, request, format=None, **kwargs):
        if 'id' in self.kwargs:
            try:
                object = PublisherInfo.objects.get(pk=uri_to_iri(self.kwargs['id']))
            except PublisherInfo.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='ID parameter is not valid')
        else:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='ID not found')

        if request.accepted_renderer.format == 'html':
            return MyAPIResponse({'record_list': [object]}, template_name='warehouse_state/publisher_detail.html')
        serializer = PublisherInfo_DbSerializer(object)
        return MyAPIResponse({'record_list': [serializer.data]})
