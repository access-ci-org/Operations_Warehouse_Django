from django.urls import path, re_path
from cider.views import *

# Define our custom URLs
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
    path(r'v1/cider_resource_id/<str:cider_resource_id>/', CiderInfrastructure_v1_Detail.as_view(), name='cider-detail-v1-id'),
    path(r'v1/info_resourceid/<str:info_resourceid>/', CiderInfrastructure_v1_Detail.as_view(), name='cider-detail-v1-infoid'),
    path(r'v1/access-active/', CiderInfrastructure_v1_ACCESSActiveList.as_view(), name='cider-accessactivelist-v1'),
    path(r'v1/coco/', CiderInfrastructure_v1_ACCESSComputeCompare.as_view(), name='cider-accesscomputecompare-v1'),
    path(r'v2/access-active/', CiderInfrastructure_v2_ACCESSActiveList.as_view(), name='cider-accessactivelist-v2'),
    path(r'v2/access-all/', CiderInfrastructure_v2_ACCESSAllList.as_view(), name='cider-accessalllist-v2'),
    path(r'v1/access-allocated/', CiderInfrastructure_v1_ACCESSAllocatedList.as_view(), name='cider-accessallocatedlist-v1'),
    path(r'v1/access-online-services/', CiderInfrastructure_v1_ACCESSOnlineServicesList.as_view(), name='cider-accessonlineserviceslist-v1'),
    path(r'v1/access-science-gateways/', CiderInfrastructure_v1_ACCESSScienceGatewaysList.as_view(), name='cider-accesssciencegatewayslist-v1'),
#    path(r'v1/compute/<str:cider_resource_id>/', CiderInfrastructure_v1_Compute_Detail.as_view(), name='cider-compute-detail-v1-infoid'),
]
