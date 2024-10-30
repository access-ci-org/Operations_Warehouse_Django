from django.contrib import admin
from cider.models import *

class CiderInfrastructure_Admin(admin.ModelAdmin):
    list_display = ('cider_resource_id', 'info_resourceid', 'cider_type', 'resource_descriptive_name')
    list_display_links = ['cider_resource_id']
    ordering = ['info_resourceid', 'cider_type']
    search_fields = ['cider_resource_id__iexact', 'info_resourceid__iexact', 'resource_descriptive_name']

class CiderGroups_Admin(admin.ModelAdmin):
    list_display = ('info_groupid', 'group_descriptive_name')
    list_display_links = ['info_groupid']
    ordering = ['info_groupid']
    search_fields = ['info_groupid__iexact', 'group_descriptive_name']

# Register your models here.
admin.site.register(CiderInfrastructure, CiderInfrastructure_Admin)
admin.site.register(CiderGroups, CiderGroups_Admin)
