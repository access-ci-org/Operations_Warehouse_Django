from django.db import models

# Create your models here.

class News(models.Model):
    URN = models.CharField(primary_key=True, max_length=128, null=False)
    Subject = models.CharField(max_length=120, null=False)
    Content = models.CharField(max_length=50000)
    NewsStart = models.DateTimeField(null=False)
    NewsEnd = models.DateTimeField(null=True, blank=True)
    # Resource full or partial outage, reconfiguration; software major or minor release; roadmap major or minor update
    NewsType = models.CharField(max_length=32, null=False)
    DistributionOptions = models.CharField(max_length=120, null=True, blank=True)
    WebURL = models.CharField(max_length=320, null=True)

    Affiliation = models.CharField(max_length=32, null=False)
    Publisher = models.ForeignKey('News_Publisher',
                related_name='newspublisher',
                on_delete=models.CASCADE, null=False)
    def __unicode__(self):
       return self.Subject
    def __str__(self):
       return str(self.URN)

# Associations may be to Type Resource, Software, Roadmap, etc.
class News_Associations(models.Model):
    NewsItem = models.ForeignKey(News,
                related_name='Associations',
                on_delete=models.CASCADE, null=False, db_index=True)
    # 'Resource', 'Software', 'Roadmap'
    AssociatedType = models.CharField(max_length=16)
    # For 'Resource' values is info_resourceid
    # For 'Software' values is TBD
    # For 'Roadmap' value is roadmap_name
    AssociatedID = models.CharField(max_length=128, db_index=True)
    def __str__(self):
       return '{}->{}/{}'.format(self.NewsItem, self.AssociatedType, self.AssociatedID)

class News_Publisher(models.Model):
    # This is the ACCESS Organization ID
    OrganizationID = models.IntegerField(primary_key=True, null=False)
    OrganizationName = models.CharField(max_length=300, null=False)
    # Organization_News URN prefix for this publisher
    NewsURNPrefix = models.CharField(max_length=64, null=False)
    def __unicode__(self):
       return self.OrganizationName
    def __str__(self):
       return '{} ({})'.format(self.OrganizationName, self.OrganizationID)
