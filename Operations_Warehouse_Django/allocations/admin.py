from django.contrib import admin
from allocations.models import *

#class Resource_Admin(admin.ModelAdmin):
#    list_display = ('ResourceID', 'SiteID')
#    list_display_links = ['ResourceID']
#    ordering = ['ResourceID', 'SiteID']
#    search_fields = ['ResourceID__iexact', 'SiteID__iexact']
#
#class Person_Admin(admin.ModelAdmin):
#    list_display = ('person_localid', 'access_id', 'last_name', 'first_name', 'middle_name', 'emails')
#    list_display_links = ['access_id']
#    ordering = ['access_id', 'last_name', 'first_name']
#    search_fields = ['person_localid__iexact', 'access_id__iexact', 'last_name', 'first_name', 'emails']
#
#class PersonLocalUsernameMap_Admin(admin.ModelAdmin):
#    list_display = ('access_id', 'resource_id', 'resource_username', 'ResourceID', 'ID')
#    list_display_links = ['access_id']
#    ordering = ['access_id', 'resource_id', 'resource_username']
#    search_fields = ['access_id__iexact', 'resource_id__iexact', 'resource_username__iexact', 'ResourceID__iexact', 'ID__iexact']
#
#class AllocationResourceMap_Admin(admin.ModelAdmin):
#    list_display = ('ResourceID', 'AllocationID')
#    list_display_links = ['ResourceID']
#    ordering = ['ResourceID', 'AllocationID']
#    search_fields = ['ResourceID__iexact', 'AllocationID__iexact']

class FieldOfScience_Admin(admin.ModelAdmin):
    list_display = ('field_of_science_id', 'field_of_science_desc', 'parent_field_of_science_id', 'fos_nsf_abbrev')
    list_display_links = ['field_of_science_id']
    ordering = ['field_of_science_desc']
    search_fields = ['field_of_science_id__iexact', 'parent_field_of_science_id__iexact', 'field_of_science_desc', 'fos_nsf_abbrev']


# Register your models here.
#admin.site.register(Resource, Resource_Admin)
#admin.site.register(Person, Person_Admin)
#admin.site.register(PersonLocalUsernameMap, PersonLocalUsernameMap_Admin)
#admin.site.register(AllocationResourceMap, AllocationResourceMap_Admin)
admin.site.register(FieldOfScience, FieldOfScience_Admin)
