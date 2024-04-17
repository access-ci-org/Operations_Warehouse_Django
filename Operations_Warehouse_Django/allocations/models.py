from django.db import models

class Resource(models.Model):
    ResourceID = models.CharField(primary_key=True,max_length=40)
    #ResourceName = models.CharField(db_index=True, max_length=120)
    SiteID = models.CharField(db_index=True, max_length=40)
    OrganizationAbbrev = models.CharField(db_index=True, max_length=40)
    OrganizationName = models.CharField(db_index=True, max_length=120)
    AmieName = models.CharField(db_index=True, max_length=40)
    PopsName = models.CharField(db_index=True, max_length=120)
    TgcdbResourceName = models.CharField(db_index=True, max_length=40)
    ResourceCode = models.CharField(db_index=True, max_length=40)
    ResourceDescription = models.CharField(db_index=True, max_length=40)
    Timestamp = models.DateTimeField(null=True)
    def __str__(self):
       return str(self.ResourceID)

class Person(models.Model):
    person_localid = models.IntegerField(primary_key=True, null=False)
    access_id = models.CharField(db_index=True, max_length=30, null=False)
    last_name = models.CharField(max_length=100, null=False)
    first_name = models.CharField(max_length=100, null=False)
    middle_name = models.CharField(max_length=60, null=True)
    is_suspended = models.BooleanField(null=False)
    organization = models.CharField(max_length=300, null=False)
    citizenships = models.CharField(max_length=300, null=True)
    emails = models.CharField(max_length=300, null=True)
    addressesJSON = models.JSONField()
    def __str__(self):
       return str(self.person_localid)

class PersonLocalUsernameMap(models.Model):
    ID = models.AutoField(primary_key=True, null=False)
    person_localid = models.IntegerField(null=False)
    access_id = models.CharField(db_index=True, max_length=30, null=False)
    resource_id = models.IntegerField(null=False)
    resource_name = models.CharField(max_length=200, null=False)
    resource_username = models.CharField(max_length=30, null=False)
    ResourceID = models.CharField(max_length=40, null=False)
    class Meta:
        unique_together = ['resource_id', 'resource_username']
    def __str__(self):
       return str(self.ID)

class AllocationResourceMap(models.Model):
    AllocationID = models.CharField(db_index=True,max_length=32)
    ResourceID = models.CharField(db_index=True, max_length=40)
    def __str__(self):
       return str(self.ResourceID)

class FieldOfScience(models.Model):
    field_of_science_id = models.IntegerField(primary_key=True, null=False)
    field_of_science_desc = models.CharField(max_length=80, null=False)
    fos_nsf_id = models.IntegerField(null=True, blank=True)
    fos_nsf_abbrev = models.CharField(max_length=10, null=True, blank=True)
    is_active = models.BooleanField(default=True, null=False)
    fos_source = models.CharField(max_length=10, null=False, blank=True)
    nsf_directorate_id = models.IntegerField(null=True, blank=True)
    nsf_directorate_name = models.CharField(max_length=80, null=True, blank=True)
    nsf_directorate_abbrev = models.CharField(max_length=10, null=True, blank=True)
    parent_field_of_science_id = models.IntegerField(null=True, blank=True)
    parent_field_of_science_desc = models.CharField(max_length=80, null=True, blank=True)
    parent_fos_nsf_id = models.IntegerField(null=True, blank=True)
    parent_fos_nsf_abbrev = models.CharField(max_length=10, null=True, blank=True)
    def __str__(self):
       return str(self.field_of_science_id)
