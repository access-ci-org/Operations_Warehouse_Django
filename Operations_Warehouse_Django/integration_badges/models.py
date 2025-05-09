from django.db import models
from cider.models import *

from django.core.files.storage import Storage
from django.core.files.base import ContentFile

import uuid


def get_current_username():
    # TODO integrate the cilogon credentials
    return "admin"

class BadgeWorkflowStatus(models.TextChoices):
    NOT_PLANNED = "not-planned", "Not Planned"
    PLANNED = "planned", "Planned"
    TASK_COMPLETED = "task-completed", "Task Completed"
    VERIFICATION_FAILED = "verification-failed", "Verification Failed"
    VERIFIED = "verified", "Verified"
    DEPRECATED = "deprecated", "Depredated"

class BadgeTaskWorkflowStatus(models.TextChoices):
    COMPLETED = "completed", "Completed"
    NOT_COMPLETED = "not-completed", "Not Completed"

class DatabaseFile(models.Model):
    file_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_name = models.CharField(max_length=100, null=True)
    file_data = models.BinaryField(null=True, editable=True)
    content_type = models.CharField(max_length=100, null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s (%d)" % (self.file_name, self.file_id)

class DatabaseFileStorage(Storage):
    def _save(self, file_id, content):
        file = DatabaseFile.objects.get(pk=file_id)
        file.file_data = content.read()
        file.content_type = content.content_type
        file.save()
        return file_id

    def _open(self, file_id, mode='rb'):
        file = DatabaseFile.objects.get(file_id=file_id)
        return ContentFile(file.file_data)

    def delete(self, file_id):
        DatabaseFile.objects.filter(file_id=file_id).delete()

    def exists(self, file_id):
        return DatabaseFile.objects.filter(file_id=file_id).exists()

    def list_dir(self, path):
        # Handle listing directories if needed, return empty list
        return [], [f.file_name for f in DatabaseFile.objects.all()]

    def size(self, file_id):
        return len(DatabaseFile.objects.get(file_id=file_id).file_data)

    def get_available_name(self, file_name, max_length=None):
        # Handle name availability if needed
        file = DatabaseFile.objects.create(file_name=file_name)
        return "%s" % file.file_id

    def url(self, file_id):
        # Handle URL generation if needed, return None
        return "/wh2/integration_badges/v1/files/%s" % file_id


class Roadmap(models.Model):
    roadmap_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    graphic = models.ImageField(null=True, storage=DatabaseFileStorage)
    executive_summary = models.TextField(null=True, blank=True)
    infrastructure_types = models.CharField(max_length=200)
    integration_coordinators = models.CharField(max_length=200)
    status = models.CharField(max_length=50)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "%s (%d)" % (self.name, self.roadmap_id)


class Badge(models.Model):
    badge_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    graphic = models.ImageField(null=True, blank=True, storage=DatabaseFileStorage)
    researcher_summary = models.TextField(null=True, blank=True)
    resource_provider_summary = models.TextField(null=True, blank=True)
    verification_summary = models.TextField(null=True, blank=True)
    verification_method = models.CharField(max_length=20)  # {Automated, Manual}
    default_badge_access_url = models.URLField(null=True, blank=True)
    default_badge_access_url_label = models.CharField(null=True, blank=True, max_length=50)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "%s (%d)" % (self.name, self.badge_id)


class Task(models.Model):
    task_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, unique=True)
    technical_summary = models.TextField(null=True, blank=True)
    implementor_roles = models.CharField(max_length=200)
    task_experts = models.CharField(max_length=200)
    detailed_instructions_url = models.URLField()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "%s (%d)" % (self.name, self.task_id)


class Badge_Prerequisite_Badge(models.Model):
    id = models.AutoField(primary_key=True)
    badge = models.ForeignKey(Badge, related_name='badge_prerequisites', on_delete=models.CASCADE)
    prerequisite_badge = models.ForeignKey(Badge, related_name='badge_required_by', on_delete=models.CASCADE)
    sequence_no = models.IntegerField()

    class Meta:
        unique_together = ('badge', 'prerequisite_badge',)


class Roadmap_Badge(models.Model):
    id = models.AutoField(primary_key=True)
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name='roadmap_badge_set',
                                related_query_name='badge_ref')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='roadmap_set',
                                related_query_name='roadmap')
    sequence_no = models.IntegerField()
    required = models.BooleanField(null=False, default=False)

    class Meta:
        unique_together = ('roadmap', 'badge',)


class Badge_Task(models.Model):
    id = models.AutoField(primary_key=True)
    badge = models.ForeignKey(Badge, related_name="badge_tasks", on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    sequence_no = models.IntegerField()
    required = models.BooleanField(null=False, default=False)

    class Meta:
        unique_together = ('badge', 'task',)


class Resource_Roadmap(models.Model):
    id = models.AutoField(primary_key=True)
    info_resourceid = models.CharField(max_length=40, null=False, blank=False)
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('info_resourceid', 'roadmap',)

class Resource_Badge(models.Model):
    id = models.AutoField(primary_key=True)
    info_resourceid = models.CharField(max_length=40, null=False, blank=False)
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    badge_access_url = models.URLField(null=True, blank=True)
    badge_access_url_label = models.CharField(null=True, blank=True, max_length=50)

    class Meta:
        unique_together = ('info_resourceid', 'roadmap', 'badge',)

    @property
    def badge_access_url_or_default(self):
        if self.badge_access_url is None:
            return self.badge.default_badge_access_url
        else:
            return self.badge_access_url

    @property
    def badge_access_url_label_or_default(self):
        if self.badge_access_url_label is None:
            return self.badge.default_badge_access_url_label
        else:
            return self.badge_access_url_label

#    @property
#    def badge(self):
#        return self.badge
#
#    @property
#    def resource(self):
#        return self.info_resourceid

    @property
    def task_status(self):
        _tast_status = []
        badge_tasks = Badge_Task.objects.filter(badge_id=self.badge_id)
        for badge_task in badge_tasks:
            task_workflow = Resource_Badge_Task_Workflow.objects.filter(
                info_resourceid=self.info_resourceid,
                roadmap_id=self.roadmap_id,
                badge_id=self.badge_id,
                task_id=badge_task.task_id
            ).order_by('-status_updated_at').first()
            if task_workflow is not None:
                _tast_status.append({
                    "task_id": badge_task.task_id,
                    "status": task_workflow.status,
                    "status_updated_by": task_workflow.status_updated_by,
                    "status_updated_at": task_workflow.status_updated_at
                })
            else:
                _tast_status.append({
                    "task_id": badge_task.task_id,
                    "status": BadgeTaskWorkflowStatus.NOT_COMPLETED,
                    "status_updated_by": None,
                    "status_updated_at": None
                })

        return _tast_status

    @property
    def workflow(self):
        return Resource_Badge_Workflow.objects.filter(
            info_resourceid=self.info_resourceid,
            roadmap_id=self.roadmap_id,
            badge_id=self.badge_id
        ).order_by('-status_updated_at').first()

    @property
    def status(self):
        if self.workflow is None:
            return BadgeWorkflowStatus.NOT_PLANNED
        return self.workflow.status

class Resource_Badge_Workflow(models.Model):
    workflow_id = models.AutoField(primary_key=True)
    info_resourceid = models.CharField(max_length=40, null=False, blank=False)
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name="badge_workflow_resource_set",
                                   related_query_name="badge_workflow_resource_ref")
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)

    status = models.CharField(null=False, max_length=20, choices=BadgeWorkflowStatus.choices)
    status_updated_by = models.CharField(null=False, max_length=50)
    status_updated_at = models.DateTimeField(null=False, auto_now_add=True)
    comment = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs):
        resource_badge = Resource_Badge.objects.filter(
            info_resourceid=self.info_resourceid,
            roadmap=self.roadmap,
            badge=self.badge )
        if resource_badge is None:
            resource_badge = Resource_Badge(
                info_resourceid=self.info_resourceid,
                roadmap=self.roadmap,
                badge=self.badge
            )
            resource_badge.save()
        super().save(*args, **kwargs)

class Resource_Badge_Task_Workflow(models.Model):
    workflow_id = models.AutoField(primary_key=True)
    info_resourceid = models.CharField(max_length=40, null=False, blank=False)
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    status = models.CharField(null=False, max_length=20, choices=BadgeTaskWorkflowStatus.choices)
    status_updated_by = models.CharField(null=False, max_length=50)
    status_updated_at = models.DateTimeField(null=False, auto_now_add=True)
    comment = models.TextField(null=True, blank=True)
