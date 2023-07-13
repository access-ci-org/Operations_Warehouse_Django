from django.db import models

################################################################################
# The abstract model(s) derived from abstract GLUE2 entities
################################################################################
class AbstractGlue2EntityModel(models.Model):
    ID = models.CharField(primary_key=True, max_length=200)
    Name = models.CharField(max_length=128, null=True)
    CreationTime = models.DateTimeField()
    Validity = models.DurationField(null=True)
    EntityJSON = models.JSONField()
    class Meta:
        abstract = True
    def __str__(self):
        return str(self.ID)

################################################################################
# GLUE2 models NOT about specific resources
################################################################################
class AdminDomain(AbstractGlue2EntityModel):
    Description = models.CharField(max_length=128, null=True)
    WWW = models.URLField(max_length=200, null=True)
    Distributed = models.BooleanField(null=True)
    Owner = models.CharField(max_length=128, null=True)

class UserDomain(AbstractGlue2EntityModel):
    Description = models.CharField(max_length=128, null=True)
    WWW = models.URLField(max_length=200, null=True)
    Level = models.IntegerField(null=True)
    UserManager = models.CharField(max_length=200, null=True)
    Member = models.CharField(max_length=64, null=True)

class AccessPolicy(AbstractGlue2EntityModel):
    Scheme = models.CharField(max_length=64, null=True)
    Rule = models.CharField(max_length=64, null=True)

class Contact(AbstractGlue2EntityModel):
    Detail = models.CharField(max_length=128)
    Type = models.CharField(max_length=16)

class Location(AbstractGlue2EntityModel):
    pass

################################################################################
# GLUE 2 models about specific resources
################################################################################
class ApplicationEnvironment(AbstractGlue2EntityModel):
    ResourceID = models.CharField(db_index=True, max_length=40)
    Description = models.CharField(max_length=512, null=True)
    AppName = models.CharField(max_length=64)
    AppVersion = models.CharField(max_length=64, default='none')

class ApplicationHandle(AbstractGlue2EntityModel):
    ResourceID = models.CharField(db_index=True, max_length=40)
    ApplicationEnvironment = models.ForeignKey(ApplicationEnvironment,
                                                related_name='applicationhandles',
                                                on_delete=models.CASCADE,
                                                null=True)
    Type = models.CharField(max_length=16)
    Value = models.CharField(max_length=80)

class AbstractService(AbstractGlue2EntityModel):
    ResourceID = models.CharField(db_index=True, max_length=40)
    ServiceType = models.CharField(max_length=32)
    Type = models.CharField(max_length=32)
    QualityLevel = models.CharField(max_length=16, null=True)

class Endpoint(AbstractGlue2EntityModel):
    ResourceID = models.CharField(db_index=True, max_length=40)
    AbstractService = models.ForeignKey(AbstractService,
                                        related_name='endpoints',
                                        on_delete=models.CASCADE,
                                        null=True)
    HealthState = models.CharField(max_length=16)
    ServingState = models.CharField(max_length=16)
    URL = models.CharField(max_length=320)
    QualityLevel = models.CharField(max_length=16, null=True)
    InterfaceVersion = models.CharField(max_length=16)
    InterfaceName = models.CharField(max_length=32)

class ComputingManager(AbstractGlue2EntityModel):
    ResourceID = models.CharField(db_index=True, max_length=40)

class ComputingShare(AbstractGlue2EntityModel):
    ResourceID = models.CharField(db_index=True, max_length=40)

class ExecutionEnvironment(AbstractGlue2EntityModel):
    ResourceID = models.CharField(db_index=True, max_length=40)

class ComputingQueue(AbstractGlue2EntityModel):
    ResourceID = models.CharField(db_index=True, max_length=40)

class ComputingActivity(AbstractGlue2EntityModel):
    ResourceID = models.CharField(db_index=True, max_length=40)
    LocalOwner = models.CharField(db_index=True, max_length=40, default='unknown')
#
class ComputingManagerAcceleratorInfo(AbstractGlue2EntityModel):
    ResourceID = models.CharField(db_index=True, max_length=40)

class ComputingShareAcceleratorInfo(AbstractGlue2EntityModel):
    ResourceID = models.CharField(db_index=True, max_length=40)

class AcceleratorEnvironment(AbstractGlue2EntityModel):
    ResourceID = models.CharField(db_index=True, max_length=40)
    Type = models.CharField(max_length=16, null=True)

# Stores every raw document received
class EntityHistory(models.Model):
    ID = models.AutoField(primary_key=True)
    DocumentType = models.CharField(db_index=True, max_length=32)
    ResourceID = models.CharField(db_index=True, max_length=40, null=True)
    ReceivedTime = models.DateTimeField()
    EntityJSON = models.JSONField()
