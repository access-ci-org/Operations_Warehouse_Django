from django.urls import path, re_path
from news.views import *

# Define our custom URLs
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
    path('v1/id/<str:ID>/', News_v1_Detail.as_view(), name='news-v1-id'),
    path('v1/', News_v1_List.as_view(), name='news-v1'),
    path('v1/publisher/<str:publisher>/', News_v1_List.as_view(), name='news-v1-publisher'),
    path('v1/affiliation/<str:affiliation>/', News_v1_List.as_view(), name='news-v1-affiliation'),
    path('v1/affiliation/<str:affiliation>/current_outages/', News_v1_Current_Outages.as_view(), name='news-v1-current-outages'),
    path('v1/affiliation/<str:affiliation>/future_outages/', News_v1_Future_Outages.as_view(), name='news-v1-future-outages'),
    path('v1/affiliation/<str:affiliation>/past_outages/', News_v1_Past_Outages.as_view(), name='news-v1-past-outages'),
    path('v1/affiliation/<str:affiliation>/all_outages/', News_v1_All_Outages.as_view(), name='news-v1-all-outages'),
    path('v1/info_groupid/<str:info_groupid>/', News_v2_Filter_Outages.as_view(), name='news-v2-filter-bygroup-outages'),
    path('v1/info_groupid/<str:info_groupid>/current_outages/', News_v2_Current_Outages.as_view(), name='news-v2-current-bygroup-outages'),
    path('v1/info_groupid/<str:info_groupid>/future_outages/', News_v2_Future_Outages.as_view(), name='news-v2-future-bygroup-outages'),
]
