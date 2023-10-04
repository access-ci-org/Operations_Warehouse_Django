from django.contrib import admin
from .models import *

# Register your models here.
class ResourceV4Catalog_Admin(admin.ModelAdmin):
    list_display = ('Affiliation', 'Name', 'ID')
    list_display_links = ['ID']
    readonly_fields = ('created_at', 'updated_at')
    search_fields = ['Affiliation__exact', 'Name', 'ID__startswith']

class ResourceV4Local_Admin(admin.ModelAdmin):
    list_display = ('Affiliation', 'LocalID', 'CreationTime', 'ID')
    list_display_links = ['ID']
    search_fields = ['Affiliation__exact', 'LocalID__exact', 'ID__startswith']
    preserve_filters = True
    fieldsets = (
        (None, {
            'fields': ('ID', 'CreationTime', 'Validity', 'Affiliation', 'CatalogMetaURL')
            }),
        ('Local Fields', {
            'fields': ('LocalID', 'LocalType', 'LocalURL', 'EntityJSON')
            })
        )

class ResourceV4_Admin(admin.ModelAdmin):
    list_display = ('Affiliation', 'Name', 'ResourceGroup', 'Type', 'ID')
    list_display_links = ['ID']
    search_fields = ['Affiliation__exact', 'Name', 'ResourceGroup__exact', 'Type__exact', 'ID__startswith']

class ResourceV4Relation_Admin(admin.ModelAdmin):
    list_display = ('FirstResourceID', 'SecondResourceID', 'RelationType', 'ID')
    list_display_links = ['ID']
    search_fields = ['FirstResourceID__startswith', 'SecondResourceID__startswith']

# Register your models here.
admin.site.register(ResourceV4Catalog, ResourceV4Catalog_Admin)
admin.site.register(ResourceV4Local, ResourceV4Local_Admin)
admin.site.register(ResourceV4, ResourceV4_Admin)
admin.site.register(ResourceV4Relation, ResourceV4Relation_Admin)
