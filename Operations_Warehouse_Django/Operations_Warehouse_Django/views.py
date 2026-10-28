from django.views.debug import technical_500_response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

import sys

# Create your views here.

class Debug_Dump(APIView):
    '''
        Display technical_500_response for debugging purposes.
    '''
    permission_classes = (IsAuthenticated,)
    schema = None
    def get(self, request, format=None, **kwargs):
        return technical_500_response(request, *sys.exc_info(), status_code=400)
