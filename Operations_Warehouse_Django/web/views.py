from django.conf import settings
from django.shortcuts import render

# Create your views here.

def index(request):
    """
    Main site page
    """
    context = {
            'app_name': settings.APP_NAME}
    return render(request, 'web/index.html', context)