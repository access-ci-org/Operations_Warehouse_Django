from django.urls import path, re_path
from cider.views import *

# Define our custom URLs
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
    path(r'v1/cider_resource_id/<str:cider_resource_id>/', CiderInfrastructure_v1_Detail.as_view(), name='cider-detail-v1-id'),
    path(r'v1/info_resourceid/<str:info_resourceid>/', CiderInfrastructure_v1_Detail.as_view(), name='cider-detail-v1-infoid'),
    path(r'v1/access-active/', CiderInfrastructure_v1_ACCESSActiveList.as_view(), name='cider-accessactivelist-v1'),
    path(r'v1/access-active/info_groupid/<str:info_groupid>/', CiderInfrastructure_v1_ACCESSActiveList.as_view(), name='cider-accessactivelist-infogroupid-v1'),
    path(r'v1/access-active-detail/info_groupid/<str:info_groupid>/', CiderInfrastructure_v1_ACCESSActiveDetailList.as_view(), name='cider-accessactivedeetail-infogroupid-v1'),
    path(r'v1/access-allocated/', CiderInfrastructure_v1_ACCESSAllocatedList.as_view(), name='cider-accessallocatedlist-v1'),
    path(r'v1/access-online-services/', CiderInfrastructure_v1_ACCESSOnlineServicesList.as_view(), name='cider-accessonlineserviceslist-v1'),
    path(r'v1/access-science-gateways/', CiderInfrastructure_v1_ACCESSScienceGatewaysList.as_view(), name='cider-accesssciencegatewayslist-v1'),
    path(r'v1/coco/', CiderInfrastructure_v1_ACCESSComputeCompare.as_view(), name='cider-accesscomputecompare-v1'),
    path(r'v1/contacts/', CiderInfrastructure_v1_ACCESSContacts.as_view(), name='cider-accesscontacts-v1'),
    path(r'v1/features/', CiderFeatures_v1_List.as_view(), name='cider-featurelist-v1'),
    path(r'v1/features/category_id/<str:category_id>/', CiderFeatures_v1_Detail.as_view(), name='cider-featuredetail-categoryid-v1'),
    path(r'v1/groups/', CiderGroups_v1_List.as_view(), name='cider-grouplist-v1'),
    path(r'v1/groups/group_id/<str:group_id>/', CiderGroups_v1_Detail.as_view(), name='cider-group-groupid-v1'),
    path(r'v1/groups/info_groupid/<str:info_groupid>/', CiderGroups_v1_Detail.as_view(), name='cider-group-info-groupid-v1'),
    path(r'v1/groups/group_type/<str:group_type>/', CiderGroups_v1_List.as_view(), name='cider-group-type-v1'),
    path(r'v1/groups/info_resourceid/<str:info_resourceid>/', CiderGroups_v1_List.as_view(), name='cider-group-infoid-v1'),
    path(r'v1/organizations/', CiderOrganizations_v1_List.as_view(), name='cider-organizationslist-v1'),
    path(r'v1/organizations/organization_id/<str:organization_id>/', CiderOrganizations_v1_Detail.as_view(), name='cider-organizationdetail-organizationid-v1'),
    path(r'v1/access-active-groups/', CiderACCESSActiveGroups_v1_List.as_view(), name='cider-accessactivegroups-v1'),
    path(r'v1/access-active-groups/type/<str:group_type>/', CiderACCESSActiveGroups_v1_List.as_view(), name='cider-accessactivegroups-bytype-v1'),
    path(r'v1/access-active-groups/group_id/<str:group_id>/', CiderACCESSActiveGroups_v1_List.as_view(), name='cider-accessactivegroups-byid-v1'),
    path(r'v1/access-active-groups/info_groupid/<str:info_groupid>/', CiderACCESSActiveGroups_v1_List.as_view(), name='cider-accessactivegroups-byinfoid-v1'),
    path(r'v2/access-active/', CiderInfrastructure_v2_ACCESSActiveList.as_view(), name='cider-accessactivelist-v2'),
    path(r'v2/access-all/', CiderInfrastructure_v2_ACCESSAllList.as_view(), name='cider-accessalllist-v2'),
]
