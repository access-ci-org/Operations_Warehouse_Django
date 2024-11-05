from django.db import models

class CiderInfrastructure(models.Model):
    cider_resource_id = models.IntegerField(primary_key=True)
    cider_type = models.CharField(max_length=16)
    info_resourceid = models.CharField(db_index=True, max_length=40)
    info_siteid = models.CharField(db_index=True, max_length=40)
    resource_descriptive_name = models.CharField(max_length=120)
    resource_description = models.CharField(max_length=4000, null=True)
    resource_status = models.JSONField()
    current_statuses = models.CharField(max_length=64)
    latest_status = models.CharField(max_length=32, null=True)
    latest_status_begin = models.DateField(null=True)
    latest_status_end = models.DateField(null=True)
    parent_resource = models.IntegerField(db_index=True, null=True)
    recommended_use = models.CharField(max_length=4000, null=True)
    access_description = models.CharField(max_length=4000, null=True)
    project_affiliation = models.CharField(max_length=64, null=True)
    provider_level = models.CharField(max_length=16, null=True)
    other_attributes = models.JSONField()
    updated_at = models.DateTimeField(null=True)
    def __str__(self):
       return str(self.cider_resource_id)

class CiderFeatures(models.Model):
    feature_category_id = models.IntegerField(primary_key=True)
    feature_category_name = models.CharField(max_length=120)
    feature_category_description = models.CharField(max_length=4000, null=True)
    features = models.JSONField(null=True, blank=True)
    other_attributes = models.JSONField(null=True, blank=True)
    def __str__(self):
       return str(self.feature_category_id)

class CiderGroups(models.Model):
    group_id = models.IntegerField(primary_key=True)
    info_groupid = models.CharField(db_index=True, max_length=40)
    group_descriptive_name = models.CharField(max_length=120)
    group_description = models.CharField(max_length=4000, null=True)
    group_logo_url = models.CharField(max_length=320, null=True, blank=True)
    group_types = models.JSONField(null=True, blank=True)
    info_resourceids = models.JSONField(null=True, blank=True)
    other_attributes = models.JSONField(null=True, blank=True)
    def __str__(self):
       return str(self.group_id)
