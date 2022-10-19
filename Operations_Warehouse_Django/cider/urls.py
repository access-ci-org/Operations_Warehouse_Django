from django.urls import path
from cider.views import *

# Define our custom URLs
# Additionally, we include login URLs for the browseable API.
urlpatterns = [
    path(r'v1/access-active/', CiderInfrastructure_v1_ACCESSActiveList.as_view(), name='cider-accessactivelist-v1'),
]
