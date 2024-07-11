from django.urls import reverse
from django.utils.encoding import uri_to_iri
from integration_badges.models import *
from rest_framework import serializers


# returns only the badge_id and name for a badge
class Integration_Badge_Serializer(serializers.ModelSerializer):
    #    badges = serializers.SerializerMethodField()

    #badges = serializers.RelatedField(many=True)

    class Meta:
        model = Integration_Badge
        fields = ('badge_id', 'name')

# returns all fields for a badge, except the prerequisites
class Integration_Badge_Extended_Serializer(serializers.ModelSerializer):

    class Meta:
        model = Integration_Badge
        fields = "__all__"

# returns the prerequisites for a badge
class Integration_Badge_Prerequisite_Serializer(serializers.ModelSerializer):

    class Meta:
        model = Integration_Badge_Prerequisite_Badge
        fields = ('badge_id', 'prerequisite_badge_id', 'sequence_no')

# returns all fields for a badge, including the prerequisites
class Integration_Badge_Full_Serializer(serializers.ModelSerializer):
    prerequisites = Integration_Badge_Prerequisite_Serializer(source='badge_prerequisites', many=True)

    class Meta:
        model = Integration_Badge
        fields = "__all__"
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        prerequisites = representation.get('prerequisites', [])
        sorted_prerequisites = sorted(prerequisites, key=lambda x: x['sequence_no'])
        representation['prerequisites'] = sorted_prerequisites
        return representation

class Integration_Roadmap_Badge_Serializer(serializers.ModelSerializer):

    class Meta:
        model = Integration_Roadmap_Badge
        fields = ('sequence_no', 'required')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['badge'] = Integration_Badge_Serializer(instance.badge_id).data
        return rep

class Integration_Roadmap_Serializer(serializers.ModelSerializer):
    #    badges = serializers.SerializerMethodField()

    badges = Integration_Roadmap_Badge_Serializer(source='badge_set', many=True)

    class Meta:
        model = Integration_Roadmap
        fields = ('roadmap_id', 'name', 'badges')
        exclude = ()

# return all the badges of a resource
class Integration_Resource_Badge_Serializer(serializers.ModelSerializer):

    class Meta:
        model = Integration_Resource_Badge
        fields = ('id', 'resource_id', 'badge_id')

# return the all information of a resource, including the list of ids of the badges
class Integration_Resource_List_Serializer(serializers.ModelSerializer):
    badges = Integration_Resource_Badge_Serializer(source='resource_badges', many=True)
    organization_name = serializers.SerializerMethodField()
    organization_url = serializers.SerializerMethodField()
    organization_logo_url = serializers.SerializerMethodField()

    class Meta:
        model = CiderInfrastructure
        fields = ('cider_resource_id', 'info_resourceid', 'cider_type', 'resource_description',
                  'resource_descriptive_name', 'badges', 
                  'organization_name', 'organization_url', 'organization_logo_url')

    def get_organization_name(self, obj) -> str:
        try:
            return obj.other_attributes['organizations'][0]['organization_name']
        except:
            return None

    def get_organization_url(self, obj) -> str:
        try:
            return obj.other_attributes['organizations'][0]['organization_url']
        except:
            return None

    def get_organization_logo_url(self, obj) -> str:
        try:
            return obj.other_attributes['organizations'][0]['organization_logo_url']
        except:
            return None

# return the roadmaps of a resource
class Integration_Resource_Roadmap_Serializer(serializers.ModelSerializer):
    roadmap = Integration_Roadmap_Serializer(source='roadmap_id')

    class Meta:
        model = Integration_Resource_Roadmap
        fields = ('id', 'resource_id', 'roadmap_id', 'roadmap')

# return all the information of a resource, including the roadmaps
class Integration_Resource_Serializer(serializers.ModelSerializer):
    roadmaps = Integration_Resource_Roadmap_Serializer(source='resource_roadmaps', many=True)
    organization_name = serializers.SerializerMethodField()
    organization_url = serializers.SerializerMethodField()
    organization_logo_url = serializers.SerializerMethodField()
    user_guide_url = serializers.SerializerMethodField()

    class Meta:
        model = CiderInfrastructure
        fields = ('cider_resource_id', 'info_resourceid', 'cider_type', 'resource_description', 'latest_status',
                  'resource_descriptive_name', 'roadmaps', 'organization_name', 'organization_url', 
                  'organization_logo_url', 'user_guide_url')
        
    def get_organization_name(self, obj) -> str:
        try:
            return obj.other_attributes['organizations'][0]['organization_name']
        except:
            return None

    def get_organization_url(self, obj) -> str:
        try:
            return obj.other_attributes['organizations'][0]['organization_url']
        except:
            return None

    def get_organization_logo_url(self, obj) -> str:
        try:
            return obj.other_attributes['organizations'][0]['organization_logo_url']
        except:
            return None
        
    def get_user_guide_url(self, object) -> str:
        try:
            return object.other_attributes['user_guide_url']
        except:
            return None

class Integration_Badge_Task_Serializer(serializers.ModelSerializer):
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Integration_Badge_Task
        fields = ['badge_id', 'sequence_no', 'tasks']

    def get_tasks(self, obj):
        return Integration_Roadmap_Task_Serializer(obj.task_id).data

class Integration_Roadmap_Task_Serializer(serializers.ModelSerializer):
    
    class Meta:
        model = Integration_Roadmap_Task
        fields = "__all__"