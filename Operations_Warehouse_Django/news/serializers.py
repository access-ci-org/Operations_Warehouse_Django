from django.urls import reverse
from django.utils.encoding import uri_to_iri
from rest_framework import serializers
import copy

from cider.models import *
from .models import *

#
# Generic News
#
class News_Associations_Embedded_Serializer(serializers.ModelSerializer):
    class Meta:
        model = News_Associations
        fields = ['AssociatedType', 'AssociatedID']
        
class News_v1_Detail_Serializer(serializers.ModelSerializer):
    PublisherID = serializers.CharField(source='Publisher.OrganizationID')
    PublisherName = serializers.CharField(source='Publisher.OrganizationName')
    Associations = News_Associations_Embedded_Serializer(many=True, read_only=True)

    class Meta:
        model = News
        fields = copy.copy([f.name for f in model._meta.get_fields(include_parents=False)])
        fields.remove(('Publisher'))
        fields.extend(('PublisherID', 'PublisherName', 'Associations'))

#
# Outages
#
class News_Associations_Embedded_ResourceID_Serializer(serializers.ModelSerializer):
    ResourceID = serializers.CharField(source='AssociatedID')
    class Meta:
        model = News_Associations
        fields = ['ResourceID']

class News_v1_Outage_Serializer(serializers.ModelSerializer):
    OutageStart = serializers.DateTimeField(source='NewsStart')
    OutageEnd = serializers.DateTimeField(source='NewsEnd')
    OutageType = serializers.SerializerMethodField()
    DistributionOptionsEmailSubscribers = serializers.SerializerMethodField()
    DistributionOptionsEmailAll = serializers.SerializerMethodField()
    DistributionOptionsPostSlack = serializers.SerializerMethodField()
    AffectedResources = News_Associations_Embedded_ResourceID_Serializer(source='Associations', many=True, read_only=True)

    class Meta:
        model = News
        fields = ['URN', 'Subject', 'Content', 'OutageStart', 'OutageEnd', 'OutageType', 'AffectedResources', \
            'DistributionOptionsEmailSubscribers', 'DistributionOptionsEmailAll', 'DistributionOptionsPostSlack']

    def get_OutageType(self, object) -> str:
        if object.NewsType == 'Outage Full':
            return('Full')
        if object.NewsType == 'Outage Partial':
            return('Partial')
        return(object.NewsType)

    def get_DistributionOptionsEmailSubscribers(self, object) -> bool:
        # The 'or' convert None to string so that split works
        dops = [opt.strip().lower() for opt in (object.DistributionOptions or '').split(',')]
        return('email only subscribers' in dops)

    def get_DistributionOptionsEmailAll(self, object) -> bool:
        dops = [opt.strip().lower() for opt in (object.DistributionOptions or '').split(',')]
        return('email everyone with access' in dops)

    def get_DistributionOptionsPostSlack(self, object) -> bool:
        dops = [opt.strip().lower() for opt in (object.DistributionOptions or '').split(',')]
        return('post to slack' in dops)

#class News_v1_List_Serializer(serializers.ModelSerializer):
#    PublisherID = serializers.CharField(source='Publisher.OrganizationID')
#    PublisherName = serializers.CharField(source='Publisher.OrganizationName')
#    Associations = News_Associations_Embedded_Serializer(many=True, read_only=True)
#
#    class Meta:
#        model = News
#        fields = copy.copy([f.name for f in model._meta.get_fields(include_parents=False)])
#        fields.remove(('Publisher'))
#        fields.extend(('PublisherID', 'PublisherName', 'Associations'))
        
class Operations_Outages_v1_List_Expand_Serializer(serializers.ModelSerializer):
    Publisher_Name = serializers.CharField(source='News_publisher.OrganizationName')
    Affected_Infrastructure = serializers.SerializerMethodField()
    class Meta:
        model = News
        fields = copy.copy([f.name for f in model._meta.get_fields(include_parents=False)])
        fields.append('Publisher_Name')
        fields.append('Affected_Infrastructure')
        
    def get_Affected_Infrastructure(self, object) -> dict:
        resources = self.newsassociations.filter(AssociatedType__exact='Resource')
        info_resourceids = resources.values_list('AssociatedID')
        cider_resources = CiderInfrastructure.objects.filter(info_resourceid__in=info_resourceids)
        return(cider_resources.values_list('cider_resource_id', 'info_resourceid', 'resource_descriptive_name'))
        
