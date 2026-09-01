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
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)
    serializer_class = ProcessingStatus_DetailURL_DbSerializer
    template_name = 'warehouse_state/list.html'
    @extend_schema(parameters=[
            OpenApiParameter('about', str, OpenApiParameter.QUERY),
            OpenApiParameter('topic', str, OpenApiParameter.QUERY),
        ])
    def get(self, request, format=None, **kwargs):
        about = kwargs.get('about', request.GET.get('about'))
        topic = kwargs.get('topic', request.GET.get('topic'))
        if about:
            try:
                objects = ProcessingStatus.objects.filter(About__exact=uri_to_iri(about))
            except ProcessingStatus.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified about not found')
        elif topic:
            try:
                objects = ProcessingStatus.objects.filter(Topic__exact=uri_to_iri(topic))
            except ProcessingStatus.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified topic not found')
        else:
            try:
                objects = ProcessingStatus.objects.all()
            except ProcessingStatus.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='No objects found')

        sort_by = request.GET.get('sort')
        try: # Primary and secondary sort
            if sort_by.endswith('ProcessingEnd'):
                objects_sorted = objects.order_by(sort_by, 'About')
            elif sort_by:   # All others
                objects_sorted = objects.order_by(sort_by, '-ProcessingEnd')
            else:
                objects_sorted = objects
        except:
            objects_sorted = objects

        serializer = ProcessingStatus_DetailURL_DbSerializer(objects_sorted, context={'request': request}, many=True)
        return MyAPIResponse({'record_list': serializer.data, 'sort_by': sort_by}, template_name='warehouse_state/list.html')

class ProcessingMetric_DbList(ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)
    serializer_class = ProcessingMetric_DetailURL_DbSerializer

    @extend_schema(parameters=[
        OpenApiParameter('about', str, OpenApiParameter.QUERY),
        OpenApiParameter('processingid', str, OpenApiParameter.QUERY),
    ])
    def get(self, request, format=None, **kwargs):
        about = kwargs.get('about', request.GET.get('about'))
        processingid = kwargs.get('processingid', request.GET.get('processingid'))
        if about:
            try:
                objects = ProcessingMetric.objects.filter(
                    About__exact=uri_to_iri(about)
                )
            except ProcessingMetric.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified about not found')
        elif processingid:
            try:
                objects = ProcessingMetric.objects.filter(
                    ProcessingID__exact=processingid
                )
            except ProcessingMetric.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified processingid not found')
        else:
            try:
                objects = ProcessingMetric.objects.all()
            except ProcessingMetric.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='No objects found')

        sort_by = request.GET.get('sort','-ProcessingTimestamp')
        try:
            if sort_by.endswith('About'):
                objects_sorted = objects.order_by(sort_by, '-ProcessingTimestamp')
            else:
                objects_sorted = objects.order_by(sort_by)
        except:
            objects_sorted = objects

        serializer = ProcessingMetric_DetailURL_DbSerializer(
            objects_sorted,
            context={'request': request},
            many=True,
        )
        return MyAPIResponse(
            {'record_list': serializer.data, 'sort_by': sort_by},
            template_name='warehouse_state/processingmetric_list.html',
        )

class ProcessingMetric_Detail(GenericAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)
    serializer_class = ProcessingMetric_DbSerializer
    def get(self, request, format=None, **kwargs):
        id = kwargs.get('id')
        if id:
            try:
                object = ProcessingMetric.objects.get(pk=uri_to_iri(id))
            except ProcessingMetric.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified id not found')
        else:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
        if request.accepted_renderer.format == 'html':
            return MyAPIResponse(
                {'record_list': [object]},
                template_name='warehouse_state/processingmetric_detail.html',
            )
        serializer = ProcessingMetric_DbSerializer(object)
        return MyAPIResponse({'record_list': [serializer.data]})

class AggregatedMetric_DbList(ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)
    serializer_class = MetricAggregation_DetailURL_DbSerializer

    @extend_schema(parameters=[
        OpenApiParameter('about', str, OpenApiParameter.QUERY),
        OpenApiParameter('metricname', str, OpenApiParameter.QUERY),
    ])
    def get(self, request, format=None, **kwargs):
        about = kwargs.get('about', request.GET.get('about'))
        metricname = kwargs.get('metricname', request.GET.get('metricname'))
        if about:
            try:
                objects = MetricAggregation.objects.filter(About__exact=uri_to_iri(about))
            except MetricAggregation.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified about not found')
        elif metricname:
            try:
                objects = MetricAggregation.objects.filter(MetricName__exact=uri_to_iri(metricname))
            except MetricAggregation.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified metricname not found')
        else:
            try:
                objects = MetricAggregation.objects.all()
            except MetricAggregation.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='No objects found')

        sort_by = request.GET.get('sort','-AggregationDate')
        try: # Primary and secondary sort
            if sort_by.endswith('AggregationDate'):
                objects_sorted = objects.order_by(sort_by, 'About')
            elif sort_by.endswith('About'):
                objects_sorted = objects.order_by(sort_by, '-AggregationDate')
            else:
                objects_sorted = objects.order_by(sort_by)
        except:
            objects_sorted = objects

        serializer = MetricAggregation_DetailURL_DbSerializer(
            objects_sorted,
            context={'request': request},
            many=True,
        )
        return MyAPIResponse(
            {'record_list': serializer.data, 'sort_by': sort_by},
            template_name='warehouse_state/aggregatedmetric_list.html',
        )


class AggregatedMetric_Detail(GenericAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)
    serializer_class = MetricAggregation_DbSerializer
    def get(self, request, format=None, **kwargs):
        id = kwargs.get('id')
        if id:
            try:
                object = MetricAggregation.objects.get(pk=uri_to_iri(id))
            except MetricAggregation.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified id not found')
        else:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')

        if request.accepted_renderer.format == 'html':
            return MyAPIResponse(
                {'record_list': [object]},
                template_name='warehouse_state/aggregatedmetric_detail.html',
            )

        serializer = MetricAggregation_DbSerializer(object)
        return MyAPIResponse({'record_list': [serializer.data]})

class ProcessingStatus_LatestList(ListAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,TemplateHTMLRenderer,)
    serializer_class = ProcessingStatus_DbSerializer
    @extend_schema(parameters=[
            OpenApiParameter('about', str, OpenApiParameter.QUERY),
            OpenApiParameter('topic', str, OpenApiParameter.QUERY),
        ])
    def get(self, request, format=None, **kwargs):
        about = kwargs.get('about', request.GET.get('about'))
        topic = kwargs.get('topic', request.GET.get('topic'))        
        if about:
            try:
                object = ProcessingStatus.objects.filter(About__exact=uri_to_iri(about)).latest('ProcessingStart')
            except ProcessingStatus.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified about not found')
        elif topic:
            try:
                object = ProcessingStatus.objects.filter(Topic__exact=uri_to_iri(topic)).latest('ProcessingStart')
            except ProcessingStatus.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified topic not found')
        else:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
        serializer = ProcessingStatus_DbSerializer(object)
        return MyAPIResponse({'record_list': [serializer.data]}, template_name='warehouse_state/list.html')

class ProcessingStatus_Detail(GenericAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,TemplateHTMLRenderer,)
    serializer_class = ProcessingStatus_DetailURL_DbSerializer
    def get(self, request, format=None, **kwargs):
        id = kwargs.get('id')
        if id:
            try: #uri_to_iri(
                object = ProcessingStatus.objects.get(pk=uri_to_iri(id))
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
        resourceid = kwargs.get('resourceidc', request.GET.get('resourceid'))   
        if resourceid:
            try:
                objects = PublisherInfo.objects.filter(ResourceID__exact=uri_to_iri(resourceid))
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
        id = kwargs.get('id')
        if id:
            try:
                object = PublisherInfo.objects.get(pk=uri_to_iri(id))
            except PublisherInfo.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='ID parameter is not valid')
        else:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='ID not found')

        if request.accepted_renderer.format == 'html':
            return MyAPIResponse({'record_list': [object]}, template_name='warehouse_state/publisher_detail.html')
        serializer = PublisherInfo_DbSerializer(object)
        return MyAPIResponse({'record_list': [serializer.data]})
