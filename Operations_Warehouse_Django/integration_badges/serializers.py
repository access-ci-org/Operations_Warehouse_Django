from django.urls import reverse
from django.utils.encoding import uri_to_iri
from integration_badges.models import *
from rest_framework import serializers

import copy
from typing import Dict, Any
import traceback


class DatabaseFile_Serializer(serializers.ModelSerializer):
    '''
    Returns DatabaseFile
    '''

    class Meta:
        model = DatabaseFile
        fields = ('file_id', 'file_name', 'file_data', 'uploaded_at')


class Integration_Badge_Serializer(serializers.ModelSerializer):
    '''
    Returns the badge_id and name of an Integration_Badge object
    '''

    class Meta:
        model = Integration_Badge
        fields = ('badge_id', 'name')


class Integration_Badge_Extended_Serializer(serializers.ModelSerializer):
    '''
    Return all fields of an Integration_Badge object
    '''

    class Meta:
        model = Integration_Badge
        fields = '__all__'


class Integration_Badge_Prerequisite_Serializer(serializers.ModelSerializer):
    '''
    Return all fields (except the internal id) of an Integration_Badge_Prerequisite_Badge 
    object, including badge_id, prerequisite_badge_id, and sequence_no
    '''

    class Meta:
        model = Integration_Badge_Prerequisite_Badge
        fields = ('badge_id', 'prerequisite_badge_id', 'sequence_no')


class Integration_Badge_Full_Serializer(serializers.ModelSerializer):
    '''
    Return all fields of an Integration_Badge object and also include the prerequisites 
    of the badge. It uses the Integration_Badge_Prerequisite_Serializer to return the 
    prerequisites.
    '''

    prerequisites = Integration_Badge_Prerequisite_Serializer(source='badge_prerequisites', many=True)

    class Meta:
        model = Integration_Badge
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        prerequisites = representation.get('prerequisites', [])
        # sort the prerequisites by sequence_no
        sorted_prerequisites = sorted(prerequisites, key=lambda x: x['sequence_no'])
        representation['prerequisites'] = sorted_prerequisites
        return representation


class Integration_Roadmap_Badge_Serializer(serializers.ModelSerializer):
    '''
    Return all fields of an Integration_Roadmap_Badge object. It includes the 
    required field that determines if the badge is required or optional by the 
    roadmap. It uses the Integration_Badge_Serializer to return the badge_id and name.
    '''

    class Meta:
        model = Integration_Roadmap_Badge
        fields = ('sequence_no', 'required')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['badge'] = Integration_Badge_Serializer(instance.badge_id).data
        return rep


class Integration_Roadmap_Serializer(serializers.ModelSerializer):
    '''
    Return all fields of an Integration_Roadmap object,
        including fields from all the roadmap-badge related items.
    '''

    badges = Integration_Roadmap_Badge_Serializer(source='badge_set', many=True)

    class Meta:
        model = Integration_Roadmap
        fields = ('roadmap_id', 'name', 'graphic', 'executive_summary', 'infrastructure_types', 'integration_coordinators', 'status', 'badges')
        exclude = ()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        badges = representation.get('badges', [])
        # Sort the badges by sequence_no
        sorted_badges = sorted(badges, key=lambda x: x['sequence_no'])
        representation['badges'] = sorted_badges
        return representation


class Integration_Resource_Badge_Serializer(serializers.ModelSerializer):
    '''
    Return all fields of an Integration_Resource_Badge object, including the badge status. 
    The badges returned are at least planned.
    '''

    status = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()

    class Meta:
        model = Integration_Resource_Badge
        fields = ('id', 'info_resourceid', 'badge_id', 'badge_access_url', 'badge_access_url_label', 'status', 'comment')

    def get_status(self, obj):
        try:
            return obj.workflow.status
        except:
            return None

    def get_comment(self, obj):
        try:
            return obj.workflow.comment
        except:
            return None


class Integration_Resource_List_Serializer(serializers.ModelSerializer):
    '''
    Return fields of a CiderInfrastructure object, including badges of the resource 
    that are at least planned.
    '''

    badges = Integration_Resource_Badge_Serializer(source='resource_badges', many=True)
    organization_name = serializers.SerializerMethodField()
    organization_url = serializers.SerializerMethodField()
    organization_logo_url = serializers.SerializerMethodField()

    class Meta:
        model = CiderInfrastructure
        # fields = ('info_resourceid', 'info_resourceid', 'cider_type', 'resource_description',
        #           'resource_descriptive_name', 'badges',
        #           'organization_name', 'organization_url', 'organization_logo_url')

        fields = ('info_resourceid', 'cider_type', 'info_resourceid', 'project_affiliation',
                  'resource_descriptive_name', 'resource_description',
                  'latest_status', 'latest_status_begin', 'latest_status_end', 'fixed_status',
                  'organization_name', 'organization_url', 'organization_logo_url',
                  'cider_view_url', 'cider_data_url', 'updated_at')

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


class Integration_Resource_Roadmap_Serializer(serializers.ModelSerializer):
    '''
    Return all roadmaps of a resource, including the roadmap_id and name. 
    Using the Integration_Roadmap_Serializer to return the roadmap_id, name, 
    and the badges of that roadmap.
    '''

    roadmap = Integration_Roadmap_Serializer(source='roadmap_id')

    class Meta:
        model = Integration_Resource_Roadmap
        fields = ('id', 'info_resourceid', 'roadmap_id', 'roadmap')


class Integration_Resource_Serializer(serializers.ModelSerializer):
    '''
    Return fields of a CiderInfrastructure object, as well as roadmaps and 
    badges statuses of associated badges that are at least planned.
    '''

    organization_name = serializers.SerializerMethodField()
    organization_url = serializers.SerializerMethodField()
    organization_logo_url = serializers.SerializerMethodField()
    user_guide_url = serializers.SerializerMethodField()
#    my_roadmaps = Integration_Resource_Roadmap.objects.filter(info_resourceid__exact=obj.info_resourceid)
#    roadmaps = Integration_Resource_Roadmap_Serializer(my_roadmaps, many=True)
    roadmaps = serializers.SerializerMethodField()
    badge_status = serializers.SerializerMethodField()

    class Meta:
        model = CiderInfrastructure
        fields = ('info_resourceid', 'info_resourceid', 'cider_type', 'resource_description', 'latest_status',
                  'resource_descriptive_name', 'organization_name', 'organization_url',
                  'organization_logo_url', 'user_guide_url', 'roadmaps', 'badge_status')

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

    def get_user_guide_url(self, obj) -> str:
        try:
            return obj.other_attributes['user_guide_url']
        except:
            return None

    def get_roadmaps(self, obj) -> Dict[str, Any]:
        try:
            my_roadmaps = Integration_Resource_Roadmap.objects.filter(info_resourceid__exact=obj.info_resourceid)
            serializer = Integration_Resource_Roadmap_Serializer(my_roadmaps, many=True)
        except:
            return None
        return serializer.data
    def get_badge_status(self, obj) -> Dict[str, Any]:
        try:
            resource_badges = Integration_Resource_Badge.objects.filter(info_resourceid__exact=obj.info_resourceid)
            badge_status = []
            for resource_badge in resource_badges:
                badge_data = {
                    'info_resourceid': resource_badge.info_resourceid,
                    'roadmap_id': resource_badge.roadmap_id_id,
                    'badge_id': resource_badge.badge_id_id,
                    'badge_access_url': resource_badge.resource_badge_access_url,
                    'badge_access_url_label': resource_badge.resource_badge_access_url_label,
                    'status': resource_badge.status,
                    'status_updated_by': resource_badge.workflow.status_updated_by if resource_badge.workflow else None,
                    'status_updated_at': resource_badge.workflow.status_updated_at if resource_badge.workflow else None,
                    'comment': resource_badge.workflow.comment if resource_badge.workflow else None,
                    'task_status': resource_badge.task_status
                }

                badge_status.append(badge_data)
            return badge_status
        except Exception as e:
            # Handle the exception
            # print(f"An error occurred: {e}")
            # traceback.print_exc()

            return None


class Integration_Task_Serializer(serializers.ModelSerializer):
    '''
    Return all fields of an Integration_Task object.
    '''

    class Meta:
        model = Integration_Task
        fields = '__all__'


class Integration_Badge_Task_Serializer(serializers.ModelSerializer):
    '''
    Return all fields of an Integration_Badge_Task object.
    '''

    task = serializers.SerializerMethodField()

    class Meta:
        model = Integration_Badge_Task
        fields = ['badge_id', 'sequence_no', 'task']

    def get_task(self, obj) -> str:
        try:
            return Integration_Task_Serializer(obj.task_id).data
        except:
            return None


class Integration_Resource_Badge_Plan_Serializer(serializers.ModelSerializer):
    '''
    Create a new Integration_Resource_Badge object.
    '''

    class Meta:
        model = Integration_Resource_Badge
        fields = ['badge_access_url', 'badge_access_url_label']

    def create(self, validated_data):
        resource = validated_data.pop('resource', None)
        badge = validated_data.pop('badge', None)

        if resource is None or badge is None:
            raise serializers.ValidationError("Resource and badge must be provided.")

        resource_badge = Integration_Resource_Badge.objects.create(
            info_resourceid=resource.info_resourceid,
            badge_id=badge,
            **validated_data
        )
        return resource_badge


class Integration_Resource_Badge_Status_Serializer(serializers.ModelSerializer):
    '''
    Return the statuses of all badges (at least planned) associated with a resource.
    '''

    badge_status = serializers.SerializerMethodField()

    class Meta:
        model = Integration_Resource_Badge
        fields = ['badge_status']

    def get_badge_status(self, obj):
        try:
            badges = obj.resource_badges.all()

            badge_status = []
            for badge in badges:
                badge_data = {
                    'badge_id': badge.badge_id.badge_id,
                    'badge_access_url': badge.badge_access_url,
                    'badge_access_url_label': badge.badge_access_url_label,
                    'status': badge.workflow.status,
                    'status_updated_by': badge.workflow.status_updated_by if badge.workflow else None,
                    'status_updated_at': badge.workflow.status_updated_at if badge.workflow else None
                }
                badge_status.append(badge_data)

            return badge_status
        except:
            return None
