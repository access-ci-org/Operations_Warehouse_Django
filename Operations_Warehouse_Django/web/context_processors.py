# myapp/context_processors.py
from django.conf import settings

def app_context_processor(request):
    return {
        'APP_NAME': getattr(settings, 'APP_NAME', 'Unknown App'),
        }