from django.urls import path, re_path
from .views import *

# Define our custom URLs
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
    path('v1/status/', ProcessingStatus_DbList.as_view(), name='processingrecord-dblist'),
    path('v1/status/about/<str:about>/', ProcessingStatus_DbList.as_view(), name='processingrecord-dblist-byabout'),
    path('v1/status/resourceid/<str:about>/', ProcessingStatus_DbList.as_view(), name='processingrecord-dblist-byabout'),
    path('v1/status/topic/<str:topic>/', ProcessingStatus_DbList.as_view(), name='processingrecord-dblist-bytopic'),
    path('v1/status/id/<str:id>/', ProcessingStatus_Detail.as_view(), name='processingrecord-detail'),
    path('v1/status/latest/about/<str:about>/', ProcessingStatus_LatestList.as_view(), name='processingrecord-latestlist-byabout'),
    path('v1/status/latest/resourceid/<str:about>/', ProcessingStatus_LatestList.as_view(), name='processingrecord-latestlist-byabout'),
    path('v1/status/latest/topic/<str:topic>/', ProcessingStatus_LatestList.as_view(), name='processingrecord-latestlist-bytopic'),
    path('v1/publisherinfo/', PublisherInfo_DbList.as_view(), name='publisherinfo-dblist'),
    path('v1/publisherinfo/id/<str:id>/', PublisherInfo_Detail.as_view(), name='publisherinfo-detail'),
    path('v1/publisherinfo/resourceid/<str:resourceid>/', PublisherInfo_DbList.as_view(), name='publisherinfo-dblist-byresourceid'),
    path('v1/metrics/', ProcessingMetric_DbList.as_view(), name='processingmetric-dblist'),
    path('v1/metrics/id/<str:id>/', ProcessingMetric_Detail.as_view(), name='processingmetric-detail'),
    path('v1/metricaggregation/', AggregatedMetric_DbList.as_view(), name='aggregatedmetric-dblist'),
    path('v1/metricaggregation/id/<str:id>/', AggregatedMetric_Detail.as_view(), name='aggregatedmetric-detail'),
]
