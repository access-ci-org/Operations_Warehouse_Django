from django.urls import path, re_path
from news.views import *

# Define our custom URLs
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
    path('v1/id/<ID>/', News_v1_Detail.as_view(), name='news-v1-id'),
    path('v1/', News_v1_List.as_view(), name='news-v1'),
    path('v1/publisher/<publisher>/', News_v1_List.as_view(), name='news-v1-publisher'),
    path('v1/affiliation/<affiliation>/', News_v1_List.as_view(), name='news-v1-affiliation'),
    path('v1/affiliation/<affiliation>/current_outages/', News_v1_Current_Outages.as_view(), name='news-v1-current-outages'),
    path('v1/affiliation/<affiliation>/future_outages/', News_v1_Future_Outages.as_view(), name='news-v1-future-outages'),
    path('v1/affiliation/<affiliation>/all_outages/', News_v1_All_Outages.as_view(), name='news-v1-all-outages'),
]
