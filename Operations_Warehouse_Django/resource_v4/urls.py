from django.urls import path
from django.views.decorators.cache import cache_page
from .views import *

# Define our custom URLs
# Additionally, we include login URLs for the browseable API.
# Special reg for resource/id/<id> in case there are slashes in the 'id'
urlpatterns = [
    path(r'v1/catalog_search/', Catalog_Search.as_view(), name='catalog-search'),
    path(r'v1/catalog/id/<str:id>/', Catalog_Detail.as_view(), name='catalog-detail'),
    path(r'v1/local/id/<str:id>/', Local_Detail.as_view(), name='local-detail-globalid'),
    path(r'v1/local_search/', Local_Search.as_view(), name='local-search'),
#    path(r'^provider/id/(?P<id>.+)/$',
#        Provider_Detail.as_view(), name='provider-detail'),
#    path(r'^provider_search/?$',
##        cache_page(60 * 60)(Provider_Search.as_view()), name='provider-search'),
#        Provider_Search.as_view(), name='provider-search'),
    path(r'v1/resource_types/', cache_page(60 * 60)(Resource_Types_List.as_view()), name='resource-types-list'),
    path(r'v1/resource/id/<str:id>/', Resource_Detail.as_view(), name='resource-detail'),
    path(r'v1/resource_search/', Resource_Search.as_view(), name='resource-search'),
#    path(r'v1/resource_esearch/', Resource_ESearch.as_view(), name='resource-esearch'),
#    path(r'^relations_cache/?$',
#        Relations_Cache.as_view(), name='relations-cache'),
]
