from django.db import models
from django.conf import settings as django_settings
from django.core.cache import caches

from elasticsearch_dsl import Document, Text, Keyword, Date, InnerDoc, Nested
from elasticsearch_dsl import Search

import re

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
class ResourceV3Catalog(models.Model):
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
class ResourceV3Local(models.Model):
    # Record management fields
    ID = models.CharField(primary_key=True, max_length=200)
    CreationTime = models.DateTimeField()
    Validity = models.DurationField(null=True)
    Affiliation = models.CharField(db_index=True, max_length=32)
    LocalID = models.CharField(db_index=True, max_length=200, null=True, blank=True)
    LocalType = models.CharField(max_length=32, null=True, blank=True)
    LocalURL = models.CharField(max_length=200, null=True, blank=True)
    # The catalog API metadata access URL (from the ResourceV3Catalog record)
    CatalogMetaURL = models.CharField(max_length=200, null=True, blank=True)
    # Local unmodified record, should conform to CatalogMetaURL -> CatalogSchemaURL
    EntityJSON = models.JSONField(null=True, blank=True)
    def __str__(self):
        return str(self.ID)

#
# Standard Resource Record used for discovery
#
class AbstractResourceV3Model(models.Model):
    # Record management fields
    # Identical to the corresponding ResourceV3Local->ID
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
        
class ResourceV3(AbstractResourceV3Model):
    def indexing(self, relations=None):
        newRels = []
        if relations:
            for i in relations:
                newRels.append({'RelatedID': i, 'RelationType': relations[i]})
        obj = ResourceV3Index(
                meta = {'id': self.ID},
                ID = self.ID,
                Affiliation = self.Affiliation,
                LocalID = self.LocalID,
                QualityLevel = self.QualityLevel,
                Name = self.Name,
                ResourceGroup = self.ResourceGroup,
                Type = self.Type,
                ShortDescription = self.ShortDescription,
                ProviderID = self.ProviderID,
                Description = self.Description,
                Topics = self.Topics,
                Keywords = self.Keywords,
                Audience = self.Audience,
                Relations = newRels,
                StartDateTime = self.StartDateTime,
                EndDateTime = self.EndDateTime
            )
        obj.save()
        return obj.to_dict(include_meta = True)
#    def delete(self):
#        obj = ResourceV3Index.get(self.ID).delete()
#        return

class ResourceV3IndexRelation(InnerDoc):
    RelatedID: Keyword()
    RelationType: Keyword()

class ResourceV3Index(Document):
    ID = Keyword()
    Affiliation = Keyword()
    LocalID = Keyword()
    QualityLevel = Keyword()
    Name = Text(fields={'Keyword': Keyword()})
    ResourceGroup = Keyword()
    Type = Keyword()
    ShortDescription = Text()
    ProviderID = Keyword()
    Description = Text()
    Topics = Text()
    Keywords = Text()
    Audience = Text()
    Relations = Nested(ResourceV3IndexRelation)
    StartDateTime = Date()
    EndDateTime = Date()
    class Index:
        name = 'resourcev3-index'

    @classmethod
    def Cache_Lookup_Relations(self):
        if not django_settings.ESCON:
            raise MyAPIException(code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Elasticsearch not available')
        ES = Search(index=self.Index.name).using(django_settings.ESCON).extra(size=0)
        ES.aggs.bucket('allRelations', 'nested', path='Relations') \
            .bucket('Relation_RelatedIDs', 'terms', field='Relations.RelatedID.keyword', size=1000)
        es_results = ES.execute()

        cache = caches[django_settings.CACHE_SERVER]
        cache_key_prefix = self.Index.name + ':relation_id_lookup:'
        count = 0
        try:
            for item in es_results.aggs['allRelations']['Relation_RelatedIDs'].buckets:
                cache_key = cache_key_prefix + item['key']
                cache_value = { 'ID': item['key'],
                                'count': item['doc_count'] }
                ES2 = Search(index=self.Index.name).using(django_settings.ESCON)
                ES2 = ES2.filter('terms', ID=list([item['key']]))
                es2_results = ES2.execute()
                if len(es2_results.hits.hits) == 1:
                    cache_value['Name'] = es2_results.hits.hits[0]['_source']['Name']
                    paren = re.findall('\(([^)]+)', cache_value['Name'])
                    if len(paren) > 0:
                        cache_value['Abbreviation'] = '-'.join(paren)
                    cache_value['Affiliation'] = es2_results.hits.hits[0]['_source']['Affiliation']
                    cache_value['ResourceGroup'] = es2_results.hits.hits[0]['_source']['ResourceGroup']
                    #cache_value['ProviderID'] = es2_results.hits.hits[0]['_source']['ProviderID']
                    if 'ProviderID' in es2_results.hits.hits[0]['_source']:
                        cache_value['ProviderID'] = es2_results.hits.hits[0]['_source']['ProviderID']
                cache.set(cache_key, cache_value, 1 * 60 * 60)  # cache for 1 hour(s)
                count += 1
        except:
            pass
        return(count)

    @classmethod
    def Lookup_Relation(self, id):
        # Lookup a cached relation, and load it into the cache if it isn't there.
        cache = caches[django_settings.CACHE_SERVER]
        cache_key_prefix = self.Index.name + ':relation_id_lookup:'
        cache_key = cache_key_prefix + id
        cache_value = cache.get(cache_key)
        if cache_value is not None:
            return cache_value

        if not django_settings.ESCON:
            raise MyAPIException(code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='Elasticsearch not available')
        ES2 = Search(index=ResourceV3Index.Index.name).using(django_settings.ESCON)
        ES2 = ES2.filter('terms', ID=list([id]))
        es2_results = ES2.execute()
        if len(es2_results.hits.hits) == 1:
            cache_value = { 'ID': id,
                            'Name': es2_results.hits.hits[0]['_source']['Name'],
                            'ResourceGroup': es2_results.hits.hits[0]['_source']['ResourceGroup'],
                            #'ProviderID': es2_results.hits.hits[0]['_source']['ProviderID'],
                            'Affiliation': es2_results.hits.hits[0]['_source']['Affiliation'] }
            if 'ProviderID' in es2_results.hits.hits[0]['_source']:
                cache_value['ProviderID'] = es2_results.hits.hits[0]['_source']['ProviderID']
            paren = re.findall('\(([^)]+)', cache_value['Name'])
            if len(paren) > 0:
                cache_value['Abbreviation'] = '-'.join(paren)
            cache.set(cache_key, cache_value, 1 * 60 * 60)  # cache for 1 hour(s)
            return cache_value
        else:
            return None

#
#  Resource Relationships
#
class ResourceV3Relation(models.Model):
    ID = models.CharField(primary_key=True, max_length=200)
    FirstResourceID = models.CharField(db_index=True, max_length=200)
    SecondResourceID = models.CharField(db_index=True, max_length=200)
    RelationType = models.CharField(max_length=32, null=False)
    def __str__(self):
        return str(self.ID)
