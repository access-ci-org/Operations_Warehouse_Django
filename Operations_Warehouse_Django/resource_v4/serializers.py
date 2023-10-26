from django.urls import reverse
from django.utils.encoding import uri_to_iri
from rest_framework import serializers
import copy

from .models import *
from .documents import *

class Catalog_List_Serializer(serializers.ModelSerializer):
    DetailURL = serializers.SerializerMethodField()
    
    def get_DetailURL(self, ResourceV4Catalog) -> str:
        http_request = self.context.get('request')
        if http_request:
            return http_request.build_absolute_uri(uri_to_iri(reverse('catalog-detail', args=[ResourceV4Catalog.ID])))
        else:
            return ''

    class Meta:
        model = ResourceV4Catalog
        fields = copy.copy([f.name for f in ResourceV4Catalog._meta.get_fields(include_parents=False)])
        fields.append('DetailURL')

class Catalog_Detail_Serializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceV4Catalog
        fields = ('__all__')

class Local_List_Serializer(serializers.ModelSerializer):
    DetailURL = serializers.SerializerMethodField()
    
    def get_DetailURL(self, ResourceV4Local) -> str:
        http_request = self.context.get('request')
        if http_request:
            return http_request.build_absolute_uri(uri_to_iri(reverse('local-detail-globalid', args=[ResourceV4Local.ID])))
        else:
            return ''

    class Meta:
        model = ResourceV4Local
        fields = copy.copy([f.name for f in ResourceV4Local._meta.get_fields(include_parents=False)])
        fields.append('DetailURL')

class Local_Detail_Serializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceV4Local
        fields = ('__all__')

#
# UNCONVERTED
#

class Resource_Detail_Serializer(serializers.ModelSerializer):
#    Relations = serializers.SerializerMethodField()
    DetailURL = serializers.SerializerMethodField()
    EntityJSON = serializers.SerializerMethodField()

#    def get_Relations(self, ResourceV4) -> list[dict[str, str]]:
#        relations = []
#        http_request = self.context.get('request')
#        try:
#            relateditems = ResourceV4Relation.objects.filter(FirstResourceID=ResourceV4.ID)
#            for ri in relateditems:
#                related = {'RelationType': ri.RelationType, 'ID': ri.SecondResourceID}
#                provider = ResourceV4Index.Lookup_Relation(ri.SecondResourceID)
#                if provider and provider.get('Name'):
#                    related['Name'] = provider.get('Name')
#                if provider and provider.get('ResourceGroup'):
#                    related['ResourceGroup'] = provider.get('ResourceGroup')
#                if provider and provider.get('ProviderID'):
#                    rp = ResourceV4Index.Lookup_Relation(provider.get('ProviderID'))
#                    if rp and rp.get('Name'):
#                        related['Provider'] = rp.get('Name')
#                if http_request:
#                    related['DetailURL'] = http_request.build_absolute_uri(uri_to_iri(reverse('resource-detail', args=[ri.SecondResourceID])))
#                relations.append(related)
#        except ResourceV4Relation.DoesNotExist:
#            pass
## Excluding Inverse Relations for now, consider adding including as InverseRelations in the future
##        try:
##            related = ResourceV4Relation.objects.filter(SecondResourceID=ResourceV4.ID)
##            for ri in related:
##                relations.append({"Type": ri.RelationType, "From.ID": ri.FirstResourceID})
##        except ResourceV4Relation.DoesNotExist:
##            pass
#        return(relations)

    def get_DetailURL(self, ResourceV4) -> str:
        http_request = self.context.get('request')
        if http_request:
            return http_request.build_absolute_uri(uri_to_iri(reverse('resource-detail', args=[ResourceV4.ID])))
        else:
            return ''

    def get_EntityJSON(self, ResourceV4) -> str:
        try:
            local = ResourceV4Local.objects.get(pk=ResourceV4.ID)
            return(local.EntityJSON)
        except ResourceV4Local.DoesNotExist:
            pass
        return(none)

    class Meta:
        model = ResourceV4
        fields = copy.copy([f.name for f in ResourceV4._meta.get_fields(include_parents=False)])
#        fields.append('Relations')
        fields.append('DetailURL')
        fields.append('EntityJSON')

class Resource_Search_Serializer(serializers.ModelSerializer):
    Provider = serializers.SerializerMethodField()
    DetailURL = serializers.SerializerMethodField()

    def get_Provider(self, ResourceV4) -> str:
#        try:
#            provider = ResourceV4Provider.objects.get(pk=ResourceV4.ProviderID)
#            if provider:
#                return({'Affiliation': provider.Affiliation, 'LocalID': provider.LocalID, 'Name': provider.Name})
#        except ResourceV4Provider.DoesNotExist:
#            pass
        return(None)

    def get_DetailURL(self, ResourceV4) -> str:
        http_request = self.context.get('request')
        if http_request:
            return http_request.build_absolute_uri(uri_to_iri(reverse('resource-detail', args=[ResourceV4.ID])))
        else:
            return ''

    class Meta:
        model = ResourceV4
        fields = copy.copy([f.name for f in ResourceV4._meta.get_fields(include_parents=False)])
        fields.append('Provider')
        fields.append('DetailURL')

class Resource_ESearch_Serializer(serializers.Serializer):
    class Meta:
        model = ResourceV4Index
        fields = ('__all__')

class Resource_Types_Serializer(serializers.Serializer):
    ResourceGroup = serializers.CharField()
    Type = serializers.CharField()
    count = serializers.IntegerField()

    class Meta:
        fields = ('__all__')
