from django.db import models
from cider.models import *

def get_current_username():
    # TODO integrate the cilogon credentials
    return "admin"

WORKFLOW_STATE = {
    "NOT_PLANNED": "Not Planned",
    "PLANNED": "Planned",
    "TASK_COMPLETED": "Task Completed",
    "VERIFICATION_FAILED": "Verification Failed",
    "VERIFIED": "Verified",
    "DEPRECATED": "Deprecated"
}

class Integration_Roadmap(models.Model):
    roadmap_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    graphic = models.ImageField()
    executive_summary = models.TextField(null=True)
    infrastructure_types = models.CharField(max_length=200)
    integration_coordinators = models.CharField(max_length=200)
    status = models.CharField(max_length=50)


class Integration_Badge(models.Model):
    badge_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    graphic = models.ImageField(null=True)
    researcher_summary = models.TextField(null=True)
    resource_provider_summary = models.TextField(null=True)
    verification_summary = models.TextField(null=True)
    verification_method = models.CharField(max_length=20) # {Automated, Manual}
    default_badge_access_url = models.URLField()
    default_badge_access_url_label = models.CharField(max_length=20)

    #prerequisite_badges = models.ManyToManyField("Integration_Badge")


class Integration_Roadmap_Task(models.Model):
    task_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    technical_summary = models.TextField(null=True)
    implementor_roles = models.CharField(max_length=200)
    task_experts = models.CharField(max_length=200)
    detailed_instructions_url = models.URLField()


class Integration_Badge_Prerequisite_Badge(models.Model):
    id = models.AutoField(primary_key=True)
    badge_id = models.ForeignKey(Integration_Badge, related_name='badge_prerequisites', on_delete=models.CASCADE)
    prerequisite_badge_id = models.ForeignKey(Integration_Badge, related_name='badge_required_by', on_delete=models.CASCADE)
    sequence_no = models.IntegerField()

    class Meta:
        unique_together = ('badge_id', 'prerequisite_badge_id',)


class Integration_Roadmap_Badge(models.Model):
    id = models.AutoField(primary_key=True)
    roadmap_id = models.ForeignKey(Integration_Roadmap, on_delete=models.CASCADE, related_name="badge_set", related_query_name="badge_ref")
    badge_id = models.ForeignKey(Integration_Badge, on_delete=models.CASCADE, related_name="roadmap_set", related_query_name="roadmap")
    sequence_no = models.IntegerField()
    required = models.BooleanField(max_length=20)

    class Meta:
        unique_together = ('roadmap_id', 'badge_id',)


class Integration_Badge_Task(models.Model):
    id = models.AutoField(primary_key=True)
    badge_id = models.ForeignKey(Integration_Badge, on_delete=models.CASCADE)
    task_id = models.ForeignKey(Integration_Roadmap_Task, on_delete=models.CASCADE)
    sequence_no = models.IntegerField()

    class Meta:
        unique_together = ('badge_id', 'task_id',)


class Integration_Resource_Roadmap(models.Model):
    id = models.AutoField(primary_key=True)
    resource_id = models.ForeignKey(CiderInfrastructure, related_name='resource_roadmaps', on_delete=models.CASCADE)
    roadmap_id = models.ForeignKey(Integration_Roadmap, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('resource_id', 'roadmap_id',)


class Integration_Workflow(models.Model):
    workflow_id = models.AutoField(primary_key=True)
    resource_id = models.ForeignKey(CiderInfrastructure, on_delete=models.CASCADE)
    badge_id = models.ForeignKey(Integration_Badge, on_delete=models.CASCADE)
    state = models.CharField(max_length=20)
    stateUpdatedBy = models.CharField(max_length=50)
    stateUpdatedAt = models.DateTimeField(auto_now_add=True)


class Integration_Resource_Badge(models.Model):
    id = models.AutoField(primary_key=True)
    resource_id = models.ForeignKey(CiderInfrastructure, related_name='resource_badges', on_delete=models.CASCADE)
    badge_id = models.ForeignKey(Integration_Badge, on_delete=models.CASCADE)
    badge_access_url = models.URLField(null=True)
    badge_access_url_label = models.CharField(max_length=20, null=True)

    class Meta:
        unique_together = ('resource_id', 'badge_id',)

    @property
    def workflow(self):
        return Integration_Workflow.objects.filter(
            resource_id=self.resource_id,
            badge_id=self.badge_id
        ).order_by('-stateUpdatedAt').first()
    
    @property
    def state(self):
        if self.workflow is None:
            return WORKFLOW_STATE["NOT_PLANNED"]
        return self.workflow.state

    def save(self, *args, **kwargs):
        if not self.pk:
            workflow = Integration_Workflow(
                state=WORKFLOW_STATE["PLANNED"],
                stateUpdatedBy=get_current_username(),
                resource_id=self.resource_id,
                badge_id=self.badge_id
            )
            workflow.save()
        super().save(*args, **kwargs)

