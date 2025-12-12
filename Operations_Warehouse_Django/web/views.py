from django.conf import settings
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.debug import technical_500_response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

import sys
import web.signals

# Create your views here.

def index(request):
    """
    Main site page
    """
    # clear any locks by current user
    
    context = {
            'app_name': settings.APP_NAME}
    return render(request, 'web/index.html', context)

class Debug_Detail(APIView):
    '''
        Dump DEBUG technical_500_response
    '''
    permission_classes = (IsAuthenticated,)
    schema = None
    def get(self, request, format=None, **kwargs):
        return technical_500_response(request, *sys.exc_info(), status_code=400)
