from django.conf import settings as django_settings
from django.core.cache import caches
from django_opensearch_dsl import Document, fields
from django_opensearch_dsl.registries import registry
from opensearchpy import InnerDoc, Search

from resource_v4.models import ResourceV4

import re

#class ResourceV4IndexRelation(InnerDoc):
#    RelatedID: fields.KeywordField()
#    RelationType: fields.KeywordField()

#    class Django:
#        model = ResourceV4Relation

@registry.register_document
class ResourceV4Index(Document):
    ID = fields.KeywordField()
    Affiliation = fields.KeywordField()
    LocalID = fields.KeywordField()
    QualityLevel = fields.KeywordField()
    Name = fields.TextField(fields={
            'Keyword': fields.KeywordField()
        })
    ResourceGroup = fields.KeywordField()
    Type = fields.KeywordField()
    ShortDescription = fields.TextField()
    ProviderID = fields.KeywordField()
    Description = fields.TextField()
    Topics = fields.TextField()
    Keywords = fields.TextField()
    Audience = fields.TextField()
    Relations = fields.NestedField(properties={
            'RelatedID': fields.KeywordField(),
            'RelationType': fields.KeywordField(),
        })
    StartDateTime = fields.DateField()
    EndDateTime = fields.DateField()

    class Django:
        model = ResourceV4

    class Index:
        name = 'resource-v4-index'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0
        }
        auto_refresh = False

    @classmethod
    def generate_id(cls, document):
        return document.ID

    @classmethod
    def Cache_Lookup_Relations(self):
        if not django_settings.OSCON:
            raise MyAPIException(code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='OpenSearch not available')
        ES = Search(index=self.Index.name).using(django_settings.OSCON).extra(size=0)
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
                ES2 = Search(index=self.Index.name).using(django_settings.OSCON)
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

        if not django_settings.OSCON:
            raise MyAPIException(code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='OpenSearch not available')
        ES2 = Search(index=ResourceV4Index.Index.name).using(django_settings.OSCON)
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
