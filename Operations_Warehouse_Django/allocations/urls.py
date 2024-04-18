from django.urls import path, re_path
from .views import *

# Define our custom URLs
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
    path('v1/fos/', Allocations_v1_fos_List.as_view(), name='accessdb-fos-list'),
    path('v1/fos/ID/<str:id>/', Allocations_v1_fos_Detail.as_view(), name='accessdb-fos-detail'),
    path('v1/fos/children/<str:parentid>/', Allocations_v1_fos_List.as_view(), name='accessdb-fos-children'),
]
