from django.urls import path, re_path
from cider.views import *

# Define our custom URLs
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
    re_path(r'v1/cider_resource_id/(?P<cider_resource_id>\w+)', CiderInfrastructure_v1_Detail.as_view(), name='cider-detail-v1-id'),
    re_path(r'v1/info_resourceid/(?P<info_resourceid>[-a-zA-Z0-9._]+)', CiderInfrastructure_v1_Detail.as_view(), name='cider-detail-v1-infoid'),
    path(r'v1/access-active/', CiderInfrastructure_v1_ACCESSActiveList.as_view(), name='cider-accessactivelist-v1'),
]
