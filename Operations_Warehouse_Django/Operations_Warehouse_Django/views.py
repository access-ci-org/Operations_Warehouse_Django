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

from django.shortcuts import redirect
from django.urls import reverse

def auto_login_view(request):
    # Change 'google' to 'github', 'facebook', etc. as needed
    provider_url = reverse('CIlogon') 
    return redirect(provider_url)
