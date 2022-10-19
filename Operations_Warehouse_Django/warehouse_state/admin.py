from django.contrib import admin
from warehouse_state.models import *

# Register your models here.

class ProcessingStatusAdmin(admin.ModelAdmin):
    list_display = ('Topic', 'About', 'ProcessingStart', 'ID')
    list_display_links = ['ID']

class ProcessingErrorAdmin(admin.ModelAdmin):
    list_display = ('Topic', 'About', 'ErrorTime', 'ID')
    list_display_links = ['ID']
    search_fields = ['Topic__iexact', 'About__iexact', 'ID__iexact']    

class PublisherInfoAdmin(admin.ModelAdmin):
    list_display = ('ResourceID', 'Type', 'Hostname', 'ID')
    list_display_links = ['ID']

# Register your models here.
admin.site.register(ProcessingStatus, ProcessingStatusAdmin)
admin.site.register(ProcessingError, ProcessingErrorAdmin)
admin.site.register(PublisherInfo, PublisherInfoAdmin)
