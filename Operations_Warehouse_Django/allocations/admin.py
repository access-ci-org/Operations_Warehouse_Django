from django.contrib import admin
from allocations.models import *

class ResourceAdmin(admin.ModelAdmin):
    list_display = ('ResourceID', 'SiteID')
    list_display_links = ['ResourceID']
    ordering = ['ResourceID', 'SiteID']
    search_fields = ['ResourceID__iexact', 'SiteID__iexact']

class PersonAdmin(admin.ModelAdmin):
    list_display = ('person_localid', 'access_id', 'last_name', 'first_name', 'middle_name', 'emails')
    list_display_links = ['access_id']
    ordering = ['access_id', 'last_name', 'first_name']
    search_fields = ['person_localid__iexact', 'access_id__iexact', 'last_name', 'first_name', 'emails']

class PersonLocalUsernameMapAdmin(admin.ModelAdmin):
    list_display = ('access_id', 'resource_id', 'resource_username', 'ResourceID', 'ID')
    list_display_links = ['access_id']
    ordering = ['access_id', 'resource_id', 'resource_username']
    search_fields = ['access_id__iexact', 'resource_id__iexact', 'resource_username__iexact', 'ResourceID__iexact', 'ID__iexact']

class AllocationResourceMapAdmin(admin.ModelAdmin):
    list_display = ('ResourceID', 'AllocationID')
    list_display_links = ['ResourceID']
    ordering = ['ResourceID', 'AllocationID']
    search_fields = ['ResourceID__iexact', 'AllocationID__iexact']

class FieldOfScienceAdmin(admin.ModelAdmin):
    list_display = ('field_of_science_id', 'field_of_science_desc', 'parent_field_of_science_id', 'fos_nsf_abbrev')
    list_display_links = ['field_of_science_id']
    ordering = ['field_of_science_desc']
    search_fields = ['field_of_science_id__iexact', 'parent_field_of_science_id__iexact', 'field_of_science_desc', 'fos_nsf_abbrev']


# Register your models here.
admin.site.register(Resource, ResourceAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(PersonLocalUsernameMap, PersonLocalUsernameMapAdmin)
admin.site.register(AllocationResourceMap, AllocationResourceMapAdmin)
admin.site.register(FieldOfScience, FieldOfScienceAdmin)
