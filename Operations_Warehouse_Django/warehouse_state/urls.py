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
]
