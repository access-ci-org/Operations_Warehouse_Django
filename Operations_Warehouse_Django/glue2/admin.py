from django.contrib import admin
from glue2.models import *

class AdminDomainAdmin(admin.ModelAdmin):
    list_display = ('Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ID__startswith']

class UserDomainAdmin(admin.ModelAdmin):
    list_display = ('Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ID__startswith']

class AccessPolicyAdmin(admin.ModelAdmin):
    list_display = ('Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ID__startswith']

class ContactAdmin(admin.ModelAdmin):
    list_display = ('Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ID__startswith']

class LocationAdmin (admin.ModelAdmin):
    list_display = ('Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ID__startswith']
#
class ApplicationEnvironmentAdmin(admin.ModelAdmin):
    list_display = ('ResourceID', 'Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ResourceID__iexact', 'ID__startswith']

class ApplicationHandleAdmin(admin.ModelAdmin):
    list_display = ('ResourceID', 'Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ResourceID__iexact', 'ID__startswith']

class AbstractServiceAdmin(admin.ModelAdmin):
    list_display = ('ResourceID', 'Name', 'ServiceType', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ResourceID__iexact', 'ID__startswith']

class EndpointAdmin(admin.ModelAdmin):
    list_display = ('ResourceID', 'Name', 'AbstractService', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ResourceID__iexact', 'ID__startswith']

class ComputingManagerAdmin(admin.ModelAdmin):
    list_display = ('ResourceID', 'Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ResourceID__iexact', 'ID__startswith']

class ExecutionEnvironmentAdmin(admin.ModelAdmin):
    list_display = ('ResourceID', 'Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ResourceID__iexact', 'ID__startswith']

class ComputingShareAdmin (admin.ModelAdmin):
    list_display = ('ResourceID', 'Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ResourceID__iexact', 'ID__startswith']

class ComputingQueueAdmin (admin.ModelAdmin):
    list_display = ('ResourceID', 'Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ResourceID__iexact', 'ID__startswith']

class ComputingActivityAdmin (admin.ModelAdmin):
    list_display = ('ResourceID', 'Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ResourceID__iexact', 'ID__startswith']
#
class ComputingManagerAcceleratorInfoAdmin(admin.ModelAdmin):
    list_display = ('ResourceID', 'Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ResourceID__iexact', 'ID__startswith']

class ComputingShareAcceleratorInfoAdmin(admin.ModelAdmin):
    list_display = ('ResourceID', 'Name', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ResourceID__iexact', 'ID__startswith']

class AcceleratorEnvironmentAdmin(admin.ModelAdmin):
    list_display = ('ResourceID', 'Name', 'Type', 'ID', 'CreationTime')
    list_display_links = ['ID']
    search_fields = ['Name', 'ResourceID__iexact', 'ID__startswith']
#
class EntityHistoryAdmin(admin.ModelAdmin):
    list_display = ('ID', 'DocumentType', 'ResourceID', 'ReceivedTime')
    list_display_links = ['ID']
    readonly_fields = ['ID']
    search_fields = ['Name', 'DocumentType__iexact', 'ResourceID__iexact', 'ID__startswith']

# Register your models here.
admin.site.register(AdminDomain, AdminDomainAdmin)
admin.site.register(UserDomain, UserDomainAdmin)
admin.site.register(AccessPolicy, AccessPolicyAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(ApplicationEnvironment, ApplicationEnvironmentAdmin)
admin.site.register(ApplicationHandle, ApplicationHandleAdmin)
admin.site.register(AbstractService, AbstractServiceAdmin)
admin.site.register(Endpoint, EndpointAdmin)
admin.site.register(ComputingManager, ComputingManagerAdmin)
admin.site.register(ExecutionEnvironment, ExecutionEnvironmentAdmin)
admin.site.register(ComputingShare, ComputingShareAdmin)
admin.site.register(ComputingQueue, ComputingQueueAdmin)
admin.site.register(ComputingActivity, ComputingActivityAdmin)
admin.site.register(ComputingManagerAcceleratorInfo, ComputingManagerAcceleratorInfoAdmin)
admin.site.register(ComputingShareAcceleratorInfo, ComputingShareAcceleratorInfoAdmin)
admin.site.register(AcceleratorEnvironment, AcceleratorEnvironmentAdmin)
admin.site.register(EntityHistory, EntityHistoryAdmin)
