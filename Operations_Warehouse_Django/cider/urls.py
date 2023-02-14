from django.urls import path, re_path
from cider.views import *

# Define our custom URLs
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
    path(r'v1/cider_resource_id/<str:cider_resource_id>/', CiderInfrastructure_v1_Detail.as_view(), name='cider-detail-v1-id'),
    path(r'v1/info_resourceid/<str:info_resourceid>/', CiderInfrastructure_v1_Detail.as_view(), name='cider-detail-v1-infoid'),
    path(r'v1/access-active/', CiderInfrastructure_v1_ACCESSActiveList.as_view(), name='cider-accessactivelist-v1'),
]
