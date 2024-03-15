from django.db import models

#
# Track processing. Applications should choose an appropriate unique ID
# We are avoiding RabbitMQ, GLUE2 or other narrower terminology so that we
#       can track processing of any type
#   Topic = what type of information (for example "glue2.applicatios")
#           for AMQP messages this is the Exchange
#   About = who the information is about (for example "bridges.psc.xsede.org")
#           for AMQP messages this is the Routing Key
#
class ProcessingStatus(models.Model):
    ID = models.CharField(primary_key=True, max_length=255)
    Topic = models.CharField(db_index=True, max_length=255)
    About = models.CharField(db_index=True, max_length=255)
    ProcessingNode = models.CharField(max_length=64)
    ProcessingApplication = models.CharField(max_length=64)
    ProcessingFunction = models.CharField(max_length=64, null=True)
    ProcessingStart = models.DateTimeField()
    ProcessingEnd= models.DateTimeField(null=True)
    ProcessingCode = models.CharField(max_length=64, null=True)
    ProcessingMessage = models.CharField(max_length=4096, null=True)
    def __str__(self):
        return str(self.ID)

#
# A record of processing errors
#
class ProcessingError(models.Model):
    ID = models.AutoField(primary_key=True)
    Topic = models.CharField(db_index=True, max_length=255)
    About = models.CharField(db_index=True, max_length=255)
    ProcessingNode = models.CharField(max_length=64)
    ProcessingApplication = models.CharField(db_index=True, max_length=64)
    ProcessingFunction = models.CharField(max_length=64, null=True)
    ErrorTime = models.DateTimeField(db_index=True)
    ErrorCode = models.CharField(max_length=64)
    ErrorMessage = models.CharField(max_length=4096, null=True)
    Reference1 = models.CharField(max_length=255, null=True)
    def __str__(self):
        return str(self.ID)

#
# A record of publishers
#   RecentHistory contains most recently processed EntityHistory.ID values
#      with the most recent first and oldest last
#
class PublisherInfo(models.Model):
    ID = models.CharField(primary_key=True, max_length=200)
    ResourceID = models.CharField(db_index=True, max_length=40)
    Type = models.CharField(max_length=32)
    Version = models.CharField(max_length=32)
    Hostname = models.CharField(max_length=64)
    Location = models.CharField(max_length=200, null=True)
    EntityJSON = models.JSONField()
    CreationTime = models.DateTimeField()
    RecentHistory = models.CharField(max_length=1024)
    def __str__(self):
        return str(self.ID)
