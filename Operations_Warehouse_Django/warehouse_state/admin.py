from django.contrib import admin
from warehouse_state.models import *

# Register your models here.

class ProcessingStatus_Admin(admin.ModelAdmin):
    list_display = ('Topic', 'About', 'ProcessingStart', 'ID')
    list_display_links = ['ID']

class ProcessingError_Admin(admin.ModelAdmin):
    list_display = ('Topic', 'About', 'ErrorTime', 'ID')
    list_display_links = ['ID']
    search_fields = ['Topic__iexact', 'About__iexact', 'ID__iexact']    

class PublisherInfo_Admin(admin.ModelAdmin):
    list_display = ('ResourceID', 'Type', 'Hostname', 'ID')
    list_display_links = ['ID']

class ProcessingMetric_Admin(admin.ModelAdmin):
    list_display = ('MetricName', 'MetricValue', 'About', 'ProcessingTimestamp', 'id')
    list_display_links = ['id']

class MetricAggregation_Admin(admin.ModelAdmin):
    list_display = ('MetricName', 'About', 'AggregationType', 'AggregationDate', 'ErrorCount', 'id')
    list_display_links = ['id']

# Register your models here.
admin.site.register(ProcessingStatus, ProcessingStatus_Admin)
admin.site.register(ProcessingError, ProcessingError_Admin)
admin.site.register(PublisherInfo, PublisherInfo_Admin)
admin.site.register(ProcessingMetric, ProcessingMetric_Admin)
admin.site.register(MetricAggregation, MetricAggregation_Admin)