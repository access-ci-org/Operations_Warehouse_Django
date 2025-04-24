from django.contrib import admin
from dal import autocomplete

from integration_badges.models import *

class DatabaseFile_Admin(admin.ModelAdmin):
    list_display = ('file_id', 'file_name', 'file_data', 'uploaded_at')
    list_display_links = ['file_name']
    ordering = ['file_name']
    search_fields = ['file_name', 'file_data', 'uploaded_at']
admin.site.register(DatabaseFile, DatabaseFile_Admin)

class Roadmap_Admin(admin.ModelAdmin):
    list_display = ('name', 'infrastructure_types', 'status', 'roadmap_id')
    list_display_links = ['name']
    ordering = ['name']
    search_fields = ['name', 'infrastructure_types']
admin.site.register(Roadmap, Roadmap_Admin)

class Badge_Admin(admin.ModelAdmin):
    list_display = ('name', 'researcher_summary', 'badge_id')
    list_display_links = ['name']
    ordering = ['name']
    search_fields = ['name', 'researcher_summary']
admin.site.register(Badge, Badge_Admin)

class Task_Admin(admin.ModelAdmin):
    list_display = ('name', 'implementor_roles', 'task_experts', 'task_id')
    list_display_links = ['name']
    ordering = ['name']
    search_fields = ['name', 'implementor_roles']
admin.site.register(Task, Task_Admin)

class Badge_Prerequisite_Badge_Admin(admin.ModelAdmin):
    autocomplete_fields = ('badge', 'prerequisite_badge',)
    list_display = ('badge_name', 'sequence_no', 'prerequisite_badge_name', 'id')
    list_display_links = ['id']
    ordering = ['badge__name', 'sequence_no', 'prerequisite_badge__name']
    search_fields = ['badge__name', 'prerequisite_badge__name']
    def badge_name(self, obj):
        return obj.badge.name
    def prerequisite_badge_name(self, obj):
        return obj.prerequisite_badge.name
admin.site.register(Badge_Prerequisite_Badge, Badge_Prerequisite_Badge_Admin)

class Roadmap_Badge_Admin(admin.ModelAdmin):
    autocomplete_fields = ('roadmap', 'badge',)
    list_display = ('roadmap_name', 'sequence_no', 'badge_name', 'required', 'id')
    list_display_links = ['id']
    ordering = ['roadmap__name', 'sequence_no', 'badge__name']
    search_fields = ['roadmap__name', 'badge__name', 'required']
    def roadmap_name(self, obj):
        return obj.roadmap.name
    def badge_name(self, obj):
        return obj.badge.name
admin.site.register(Roadmap_Badge, Roadmap_Badge_Admin)


class Badge_Task_Admin(admin.ModelAdmin):
    autocomplete_fields = ('badge', 'task',)
    list_display = ('badge_name', 'sequence_no', 'task_name', 'id')
    list_display_links = ['id']
    ordering = ['badge__name', 'sequence_no', 'task__name']
    search_fields = ['badge__name', 'task__name']
    def badge_name(self, obj):
        return obj.badge.name
    def task_name(self, obj):
        return obj.task.name
admin.site.register(Badge_Task, Badge_Task_Admin)


class Resource_Roadmap_Admin(admin.ModelAdmin):
    autocomplete_fields = ('roadmap',)
    list_display = ('info_resourceid', 'roadmap_name', 'id')
    list_display_links = ['id']
    ordering = ['info_resourceid', 'roadmap__name']
    search_fields = ['info_resourceid', 'roadmap__name']
    def roadmap_name(self, obj):
        return obj.roadmap.name
admin.site.register(Resource_Roadmap, Resource_Roadmap_Admin)


class Resource_Badge_Admin(admin.ModelAdmin):
    autocomplete_fields = ('roadmap', 'badge')
    list_display = ('info_resourceid', 'roadmap_name', 'badge_name', 'id')
    list_display_links = ['id']
    ordering = ['info_resourceid', 'roadmap__name', 'badge__name']
    search_fields = ['info_resourceid', 'roadmap__name', 'badge__name']
    def roadmap_name(self, obj):
        return obj.roadmap.name
    def badge_name(self, obj):
        return obj.badge.name
admin.site.register(Resource_Badge, Resource_Badge_Admin)


class Resource_Badge_Workflow_Admin(admin.ModelAdmin):
    autocomplete_fields = ('roadmap', 'badge',)
    list_display = ('info_resourceid', 'roadmap_name', 'badge_name', 'status_updated_at', 'status', 'workflow_id')
    list_display_links = ['workflow_id']
    ordering = ['info_resourceid', 'roadmap__name', 'badge__name', '-status_updated_at']
    search_fields = ['info_resourceid', 'roadmap__name', 'badge__name', 'status', 'status_updated_by']
    def roadmap_name(self, obj):
        return obj.roadmap.name
    def badge_name(self, obj):
        return obj.badge.name
admin.site.register(Resource_Badge_Workflow, Resource_Badge_Workflow_Admin)


class Resource_Badge_Task_Workflow_Admin(admin.ModelAdmin):
    autocomplete_fields = ('roadmap', 'badge', 'task')
    list_display = ('info_resourceid', 'roadmap_name', 'badge_name', 'task_name', 'status_updated_at', 'status', 'workflow_id')
    list_display_links = ['workflow_id']
    ordering = ['info_resourceid', 'roadmap__name', 'badge__name', 'task__name', '-status_updated_at']
    search_fields = ['info_resourceid', 'roadmap__name', 'badge__name', 'task__name', 'status', 'status_updated_by']
    def roadmap_name(self, obj):
        return obj.roadmap.name
    def badge_name(self, obj):
        return obj.badge.name
    def task_name(self, obj):
        return obj.task.name
admin.site.register(Resource_Badge_Task_Workflow, Resource_Badge_Task_Workflow_Admin)
