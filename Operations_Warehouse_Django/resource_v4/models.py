from django.db import models

################################################################################
# GLUE2 identifiers (AbstraceGlue2Entity)
#   ID: Unique URI ID across all models and resource types
#   Name: Short descriptive name
#   CreationTime: When the resource was created or refreshed in this catalog
#   Validity: How long after CreationTime to expire the resource
# Global attributes
#   Affiliation: Short descriptive publishing organization name (domain like)
################################################################################
#
# Catalogs that resource information come from
#
class ResourceV4Catalog(models.Model):
    # Record management fields
    ID = models.CharField(primary_key=True, max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Content fields
    Name = models.CharField(max_length=255, null=False, blank=False)
    Affiliation = models.CharField(max_length=32, null=False)
    ShortDescription = models.CharField(max_length=1000, null=False, blank=False)
    # The catalog API metadata access URL (self reference URL)
    CatalogMetaURL = models.URLField(max_length=200, blank=True)
    # The catalog local user interface URL
    CatalogUserURL = models.URLField(max_length=200, blank=True)
    # The catalog API for software (not URLField so we can do sql:<etc> and other URIs)
    CatalogAPIURL = models.CharField(max_length=200, blank=True)
    # The schema for the catalog API for software
    CatalogSchemaURL = models.URLField(max_length=200, blank=True)
    def __str__(self):
        return str(self.ID)

#
# Local Resource Record (unmodified in EntityJSON)
#
class ResourceV4Local(models.Model):
    # Record management fields
    ID = models.CharField(primary_key=True, max_length=200)
    CreationTime = models.DateTimeField()
    Validity = models.DurationField(null=True)
    Affiliation = models.CharField(db_index=True, max_length=32)
    LocalID = models.CharField(db_index=True, max_length=200, null=True, blank=True)
    LocalType = models.CharField(max_length=32, null=True, blank=True)
    LocalURL = models.CharField(max_length=400, null=True, blank=True)
    # The catalog API metadata access URL (from the ResourceV4Catalog record)
    CatalogMetaURL = models.CharField(max_length=200, null=True, blank=True)
    # Local unmodified record, should conform to CatalogMetaURL -> CatalogSchemaURL
    EntityJSON = models.JSONField(null=True, blank=True)
    def __str__(self):
        return str(self.ID)

#
# Standard Resource Record used for discovery
#
class AbstractResourceV4Model(models.Model):
    # Record management fields
    # Identical to the corresponding ResourceV4Local->ID
    ID = models.CharField(primary_key=True, max_length=200)
    Affiliation = models.CharField(max_length=32)
    LocalID = models.CharField(max_length=200, null=True, blank=True)
    QualityLevel = models.CharField(max_length=16, null=True)
    # Base content fields
    Name = models.CharField(max_length=255)
    ResourceGroup = models.CharField(max_length=64)
    Type = models.CharField(max_length=64)
    ShortDescription = models.CharField(max_length=1200, null=True, blank=True)
    ProviderID = models.CharField(max_length=200, null=True, blank=True)
    Description = models.CharField(max_length=24000, null=True, blank=True)
    Topics = models.CharField(max_length=1000, null=True, blank=True)
    Keywords = models.CharField(max_length=1000, null=True, blank=True)
    Audience = models.CharField(max_length=200, null=True, blank=True)
    # Event content fields
    StartDateTime = models.DateTimeField(null=True, blank=True)
    EndDateTime = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return str(self.ID)
        
class ResourceV4(AbstractResourceV4Model):
    pass

#
#  Resource Relationships
#
class ResourceV4Relation(models.Model):
    ID = models.CharField(primary_key=True, max_length=200)
    FirstResourceID = models.CharField(db_index=True, max_length=200)
    SecondResourceID = models.CharField(db_index=True, max_length=200)
    RelationType = models.CharField(max_length=32, null=False)
    def __str__(self):
        return str(self.ID)
