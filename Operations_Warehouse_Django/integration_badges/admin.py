from django.contrib import admin
from dal import autocomplete

from integration_badges.models import *

class DatabaseFile_Admin(admin.ModelAdmin):
    list_display = ('file_id', 'file_name', 'file_data', 'uploaded_at')
    list_display_links = ['file_name']
    ordering = ['file_name']
    search_fields = ['file_name', 'file_data', 'uploaded_at']

# Register your models here.
admin.site.register(DatabaseFile, DatabaseFile_Admin)

class Integration_Roadmap_Admin(admin.ModelAdmin):
    list_display = ('roadmap_id', 'name', 'graphic', 'executive_summary', 'infrastructure_types',
                    'integration_coordinators', 'status')
    list_display_links = ['name']
    ordering = ['name', 'roadmap_id']
    search_fields = ['name', 'executive_summary']

# Register your models here.
admin.site.register(Integration_Roadmap, Integration_Roadmap_Admin)


class Integration_Badge_Admin(admin.ModelAdmin):
    list_display = ('badge_id', 'name', 'graphic', 'researcher_summary', 'resource_provider_summary',
                    'verification_summary', 'verification_method',
                    'default_badge_access_url', 'default_badge_access_url_label')
    list_display_links = ['name']
    ordering = ['name', 'badge_id']
    search_fields = ['name', 'researcher_summary', 'resource_provider_summary']

# Register your models here.
admin.site.register(Integration_Badge, Integration_Badge_Admin)


class Integration_Roadmap_Badge_Admin(admin.ModelAdmin):
    autocomplete_fields = ('roadmap_id', 'badge_id',)
    list_display = ('id', 'roadmap_id', 'badge_id', 'sequence_no', 'required')
    list_display_links = ['id']
    ordering = ['roadmap_id', 'badge_id']
    search_fields = ['id', 'roadmap_id', 'badge_id', 'sequence_no', 'required']

# Register your models here.
admin.site.register(Integration_Roadmap_Badge, Integration_Roadmap_Badge_Admin)

class Integration_Task_Admin(admin.ModelAdmin):
    list_display = ('task_id', 'name', 'technical_summary', 'implementor_roles', 'task_experts', 'detailed_instructions_url')
    list_display_links = ['name']
    ordering = ['task_id']
    search_fields = ['name', 'technical_summary']

# Register your models here.
admin.site.register(Integration_Task, Integration_Task_Admin)

class Integration_Badge_Prerequisite_Badge_Admin(admin.ModelAdmin):
    autocomplete_fields = ('badge_id', 'prerequisite_badge_id',)
    list_display = ('id', 'badge_id', 'prerequisite_badge_id', 'sequence_no')
    list_display_links = ['id']
    ordering = ['badge_id', 'prerequisite_badge_id']
    search_fields = ['id', 'badge_id', 'prerequisite_badge_id', 'sequence_no']

# Register your models here.
admin.site.register(Integration_Badge_Prerequisite_Badge, Integration_Badge_Prerequisite_Badge_Admin)


class Integration_Badge_Task_Admin(admin.ModelAdmin):
    autocomplete_fields = ('badge_id', 'task_id',)
    list_display = ('id', 'badge_id', 'task_id', 'sequence_no')
    list_display_links = ['id']
    ordering = ['badge_id', 'task_id']
    search_fields = ['id', 'badge_id', 'task_id', 'sequence_no']

# Register your models here.
admin.site.register(Integration_Badge_Task, Integration_Badge_Task_Admin)


class Integration_Resource_Roadmap_Admin(admin.ModelAdmin):
    autocomplete_fields = ('roadmap_id',)
    list_display = ('id', 'info_resourceid', 'roadmap_id')
    list_display_links = ['id']
    ordering = ['info_resourceid', 'roadmap_id']
    search_fields = ['id', 'info_resourceid', 'roadmap_id']


# Register your models here.
admin.site.register(Integration_Resource_Roadmap, Integration_Resource_Roadmap_Admin)


class Integration_Resource_Badge_Admin(admin.ModelAdmin):
    autocomplete_fields = ('roadmap_id', 'badge_id',)
    list_display = ('id', 'info_resourceid', 'roadmap_id', 'badge_id')
    list_display_links = ['id']
    ordering = ['info_resourceid', 'roadmap_id', 'badge_id']
    search_fields = ['info_resourceid', 'roadmap_id', 'badge_id']

# Register your models here.
admin.site.register(Integration_Resource_Badge, Integration_Resource_Badge_Admin)


class Integration_Badge_Workflow_Admin(admin.ModelAdmin):
    autocomplete_fields = ('roadmap_id', 'badge_id',)
    list_display = ('workflow_id', 'info_resourceid', 'roadmap_id', 'badge_id', 'status', 'status_updated_by', 'status_updated_at')
    list_display_links = ['workflow_id']
    ordering = ['info_resourceid', 'roadmap_id', 'badge_id', 'workflow_id']
    search_fields = ['info_resourceid', 'roadmap_id', 'badge_id', 'status', 'status_updated_by']

# Register your model here.
admin.site.register(Integration_Badge_Workflow, Integration_Badge_Workflow_Admin)


class Integration_Badge_Task_Workflow_Admin(admin.ModelAdmin):
    autocomplete_fields = ('roadmap_id', 'badge_id', 'task_id')
    list_display = ('workflow_id', 'info_resourceid', 'roadmap_id', 'badge_id', 'task_id', 'status', 'status_updated_by', 'status_updated_at')
    list_display_links = ['workflow_id']
    ordering = ['info_resourceid', 'roadmap_id', 'badge_id', 'task_id', 'workflow_id']
    search_fields = ['info_resourceid', 'roadmap_id', 'badge_id', 'task_id', 'status', 'status_updated_by']

# Register your model here.
admin.site.register(Integration_Badge_Task_Workflow, Integration_Badge_Task_Workflow_Admin)
