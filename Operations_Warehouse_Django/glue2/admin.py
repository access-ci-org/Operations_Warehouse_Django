from django.contrib import admin
from glue2.models import *

class AdminDomain_Admin(admin.ModelAdmin):
    list_display = ('Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ID__startswith']

class UserDomain_Admin(admin.ModelAdmin):
    list_display = ('Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ID__startswith']

class AccessPolicy_Admin(admin.ModelAdmin):
    list_display = ('Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ID__startswith']

class Contact_Admin(admin.ModelAdmin):
    list_display = ('Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ID__startswith']

class Location_Admin (admin.ModelAdmin):
    list_display = ('Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ID__startswith']
#
class ApplicationEnvironment_Admin(admin.ModelAdmin):
    list_display = ('ResourceID', 'Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ResourceID__iexact', 'ID__startswith']

class ApplicationHandle_Admin(admin.ModelAdmin):
    list_display = ('ResourceID', 'Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ResourceID__iexact', 'ID__startswith']

class AbstractService_Admin(admin.ModelAdmin):
    list_display = ('ResourceID', 'Name', 'ServiceType', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ResourceID__iexact', 'ID__startswith']

class Endpoint_Admin(admin.ModelAdmin):
    list_display = ('ResourceID', 'Name', 'AbstractService', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ResourceID__iexact', 'ID__startswith']

class ComputingManager_Admin(admin.ModelAdmin):
    list_display = ('ResourceID', 'Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ResourceID__iexact', 'ID__startswith']

class ExecutionEnvironment_Admin(admin.ModelAdmin):
    list_display = ('ResourceID', 'Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ResourceID__iexact', 'ID__startswith']

class ComputingShare_Admin (admin.ModelAdmin):
    list_display = ('ResourceID', 'Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ResourceID__iexact', 'ID__startswith']

class ComputingQueue_Admin (admin.ModelAdmin):
    list_display = ('ResourceID', 'Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ResourceID__iexact', 'ID__startswith']

class ComputingActivity_Admin (admin.ModelAdmin):
    list_display = ('ResourceID', 'Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ResourceID__iexact', 'ID__startswith']
#
class ComputingManagerAcceleratorInfo_Admin(admin.ModelAdmin):
    list_display = ('ResourceID', 'Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ResourceID__iexact', 'ID__startswith']

class ComputingShareAcceleratorInfo_Admin(admin.ModelAdmin):
    list_display = ('ResourceID', 'Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ResourceID__iexact', 'ID__startswith']

class AcceleratorEnvironment_Admin(admin.ModelAdmin):
    list_display = ('ResourceID', 'Name', 'Type', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ResourceID__iexact', 'ID__startswith']
#
class EntityHistory_Admin(admin.ModelAdmin):
    list_display = ('ID', 'DocumentType', 'ResourceID', 'ReceivedTime')
    list_display_links = ['ID']
    readonly_fields = ['ID']
    search_fields = ['Name', 'DocumentType__iexact', 'ResourceID__iexact', 'ID__startswith']

# Register your models here.
admin.site.register(AdminDomain, AdminDomain_Admin)
admin.site.register(UserDomain, UserDomain_Admin)
admin.site.register(AccessPolicy, AccessPolicy_Admin)
admin.site.register(Contact, Contact_Admin)
admin.site.register(Location, Location_Admin)
admin.site.register(ApplicationEnvironment, ApplicationEnvironment_Admin)
admin.site.register(ApplicationHandle, ApplicationHandle_Admin)
admin.site.register(AbstractService, AbstractService_Admin)
admin.site.register(Endpoint, Endpoint_Admin)
admin.site.register(ComputingManager, ComputingManager_Admin)
admin.site.register(ExecutionEnvironment, ExecutionEnvironment_Admin)
admin.site.register(ComputingShare, ComputingShare_Admin)
admin.site.register(ComputingQueue, ComputingQueue_Admin)
admin.site.register(ComputingActivity, ComputingActivity_Admin)
admin.site.register(ComputingManagerAcceleratorInfo, ComputingManagerAcceleratorInfo_Admin)
admin.site.register(ComputingShareAcceleratorInfo, ComputingShareAcceleratorInfo_Admin)
admin.site.register(AcceleratorEnvironment, AcceleratorEnvironment_Admin)
admin.site.register(EntityHistory, EntityHistory_Admin)
