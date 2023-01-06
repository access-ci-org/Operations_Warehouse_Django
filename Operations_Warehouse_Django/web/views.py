from django.conf import settings
from django.shortcuts import render

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
