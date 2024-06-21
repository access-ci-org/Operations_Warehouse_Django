from django.contrib import admin

from integration_badges.models import *

class Integration_Roadmap_Admin(admin.ModelAdmin):
    list_display = ('roadmap_id', 'name', 'graphic', 'executive_summary', 'infrastructure_types',
                    'integration_coordinators', 'status')
    list_display_links = ['roadmap_id']
    ordering = ['name', 'roadmap_id']
    search_fields = ['name', 'executive_summary']

# Register your models here.
admin.site.register(Integration_Roadmap, Integration_Roadmap_Admin)

class Integration_Badge_Admin(admin.ModelAdmin):
    list_display = ('badge_id', 'name', 'graphic', 'researcher_summary', 'resource_provider_summary',
                    'verification_summary', 'verification_method',
                    'default_badge_access_url', 'default_badge_access_url_label')
    list_display_links = ['badge_id']
    ordering = ['name', 'badge_id']
    search_fields = ['name', 'researcher_summary', 'resource_provider_summary']

# Register your models here.
admin.site.register(Integration_Badge, Integration_Badge_Admin)


class Integration_Roadmap_Badge_Admin(admin.ModelAdmin):
    list_display = ('id', 'roadmap_id', 'badge_id', 'sequence_no', 'required')
    list_display_links = ['id']
    ordering = ['roadmap_id', 'badge_id']
    search_fields = ['id', 'roadmap_id', 'badge_id', 'sequence_no', 'required']

# Register your models here.
admin.site.register(Integration_Roadmap_Badge, Integration_Roadmap_Badge_Admin)

class Integration_Roadmap_Task_Admin(admin.ModelAdmin):
    list_display = ('task_id', 'name', 'technical_summary', 'implementor_roles', 'task_experts', 'detailed_instructions_url')
    list_display_links = ['task_id']
    ordering = ['task_id']
    search_fields = ['name', 'technical_summary']

# Register your models here.
admin.site.register(Integration_Roadmap_Task, Integration_Roadmap_Task_Admin)

class Integration_Badge_Prerequisite_Badge_Admin(admin.ModelAdmin):
    list_display = ('id', 'badge_id', 'prerequisite_badge_id', 'sequence_no')
    list_display_links = ['id']
    ordering = ['badge_id', 'prerequisite_badge_id']
    search_fields = ['id', 'badge_id', 'prerequisite_badge_id', 'sequence_no']

# Register your models here.
admin.site.register(Integration_Badge_Prerequisite_Badge, Integration_Badge_Prerequisite_Badge_Admin)


class Integration_Badge_Task_Admin(admin.ModelAdmin):
    list_display = ('id', 'badge_id', 'task_id', 'sequence_no')
    list_display_links = ['id']
    ordering = ['badge_id', 'task_id']
    search_fields = ['id', 'badge_id', 'task_id', 'sequence_no']

# Register your models here.
admin.site.register(Integration_Badge_Task, Integration_Badge_Task_Admin)


class Integration_Resource_Roadmap_Admin(admin.ModelAdmin):
    list_display = ('id', 'resource_id', 'roadmap_id')
    list_display_links = ['id']
    ordering = ['resource_id', 'roadmap_id']
    search_fields = ['id', 'resource_id', 'roadmap_id']

# Register your models here.
admin.site.register(Integration_Resource_Roadmap, Integration_Resource_Roadmap_Admin)


class Integration_Resource_Badge_Admin(admin.ModelAdmin):
    list_display = ('id', 'resource_id', 'badge_id')
    list_display_links = ['id']
    ordering = ['resource_id', 'badge_id']
    search_fields = ['id', 'resource_id', 'badge_id']

# Register your models here.
admin.site.register(Integration_Resource_Badge, Integration_Resource_Badge_Admin)


