from django.urls import reverse
from django.utils.encoding import uri_to_iri
from rest_framework import serializers

from integration_badges.models import *

import copy
from typing import Dict, Any

# _Detail_ includes all fields from a Model
# _Full_ includes fields from a model and dependent Models (i.e. roadmap badges, badge tasks, ..)
# _Min_ serializers include minimum set of fields

class DatabaseFile_Serializer(serializers.ModelSerializer):
    '''
    Returns DatabaseFile
    '''

    class Meta:
        model = DatabaseFile
        fields = ('file_id', 'file_name', 'file_data', 'uploaded_at')


class Task_Serializer(serializers.ModelSerializer):
    '''
    Return all fields of an Task object.
    '''

    class Meta:
        model = Task
        fields = '__all__'


class Badge_Task_Full_Serializer(serializers.ModelSerializer):
    '''
    Return all fields of an Badge_Task object.
    '''

    task = Task_Serializer()

    class Meta:
        model = Badge_Task
        fields = ('badge_id', 'sequence_no', 'task', 'required')


class Badge_Min_Serializer(serializers.ModelSerializer):
    '''
    Returns Badge badge_id and name only
    '''

    class Meta:
        model = Badge
        fields = ('badge_id', 'name')


class Badge_Detail_Serializer(serializers.ModelSerializer):
    '''
    Return all Badge fields
    '''

    class Meta:
        model = Badge
        fields = '__all__'


class Badge_Prerequisite_Detail_Serializer(serializers.ModelSerializer):
    '''
    Returns Badge prerequisite badge selected fields
    '''

    badge_id = serializers.IntegerField(source='prerequisite_badge_id')

    class Meta:
        model = Badge_Prerequisite_Badge
        fields = ('badge_id', 'sequence_no')


class Badge_Task_Detail_Serializer(serializers.ModelSerializer):
    '''
    Returns Badge prerequisite badge selected fields
    '''

    class Meta:
        model = Badge_Task
        fields = ('task_id', 'required', 'sequence_no')


class Task_Badge_Detail_Serializer(serializers.ModelSerializer):
    '''
    Returns Badge prerequisite badge selected fields
    '''

    class Meta:
        model = Badge_Task
        fields = ('badge_id', 'required', 'sequence_no')


class Badge_Full_Serializer(serializers.ModelSerializer):
    '''
    Return all Badge fields and pre-requisites
    '''

    prerequisites = Badge_Prerequisite_Detail_Serializer(source='badge_prerequisites', many=True)
    tasks = Badge_Task_Detail_Serializer(source='badge_tasks', many=True)

    class Meta:
        model = Badge
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        prerequisites = representation.get('prerequisites', [])
        # sort the prerequisites by sequence_no
        sorted_prerequisites = sorted(prerequisites, key=lambda x: x['sequence_no'])
        representation['prerequisites'] = sorted_prerequisites


        tasks = representation.get('tasks', [])
        # sort the tasks by sequence_no
        sorted_tasks = sorted(tasks, key=lambda x: x['sequence_no'])
        representation['tasks'] = sorted_tasks


        return representation


class Task_Full_Serializer(serializers.ModelSerializer):
    '''
    Return all Badge fields and pre-requisites
    '''

    badges = Task_Badge_Detail_Serializer(source='task_badges', many=True)

    class Meta:
        model = Task
        fields = '__all__'


class Roadmap_Min_Serializer(serializers.ModelSerializer):
    '''
    Returns Roadmap roadmap_id and name only
    '''

    class Meta:
        model = Roadmap
        fields = ('roadmap_id', 'name')


class Roadmap_Badge_Serializer(serializers.ModelSerializer):
    '''
    Returns Roadmap related Badge sequence_no and required, plus basic Badge_Min_Serializer about the badge
    '''

    badge_id = serializers.IntegerField()

    class Meta:
        model = Roadmap_Badge
        fields = ('sequence_no', 'required', 'badge_id')


class Roadmap_Review_Badge_Extended_Serializer(serializers.ModelSerializer):
    '''
    Return all Badge fields and pre-requisites
    '''

    prerequisite_list = serializers.SerializerMethodField()
    tasks = Badge_Task_Full_Serializer(source='badge_tasks', many=True)

    class Meta:
        model = Badge
        fields = '__all__'
        extra_fields = ['prerequisite_list', 'tasks']

    def get_prerequisite_list(self, obj) -> str:
        try:
            pre_reqs = [o.prerequisite_badge for o in Badge_Prerequisite_Badge.objects.filter(badge_id=obj.badge_id)]
            pre_req_names = ', '.join([o.name for o in pre_reqs])
            return pre_req_names
        except:
            return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        prerequisites = representation.get('prerequisites', [])
        # sort the prerequisites by sequence_no
        sorted_prerequisites = sorted(prerequisites, key=lambda x: x['sequence_no'])
        representation['prerequisites'] = sorted_prerequisites
        return representation


class Roadmap_Review_Badge_Serializer(serializers.ModelSerializer):
    '''
    Returns Roadmap related Badge sequence_no and required, plus basic Badge_Min_Serializer about the badge
    '''

    badge = Roadmap_Review_Badge_Extended_Serializer(many=False)

    class Meta:
        model = Roadmap_Badge
        fields = '__all__'


class Roadmap_Review_Serializer(serializers.ModelSerializer):
    '''
    Return Roadmap information for content review
    '''
    badges = Roadmap_Review_Badge_Serializer(source='roadmap_badge_set', many=True)

    class Meta:
        model = Roadmap
        fields = '__all__'


class Badge_Review_Resource_Serializer(serializers.ModelSerializer):
    '''
    Return Badge resource information for content review
    '''
    class Meta:
        model = Resource_Badge
        fields = '__all__'
#        fields = ('info_resourceid', 'badge', 'badge_access_url', 'badge_access_url_label')

class Badge_Review_Serializer(serializers.ModelSerializer):
    '''
    Return Badge information for content review
    '''
    class Meta:
        model = Badge
        fields = '__all__'

class Badge_Review_Extended_Serializer(serializers.ModelSerializer):
    '''
    Return Badge information for content review
    '''
    resources = Badge_Review_Resource_Serializer(source='badge_resource_set', many=True)

    class Meta:
        model = Badge
        fields = '__all__'


class Roadmap_Review_Nav_Serializer(serializers.ModelSerializer):
    '''
    Return Roadmap information for content review navigation
    '''
    roadmap_detail_url = serializers.SerializerMethodField()

    class Meta:
        model = Roadmap
        fields = ('roadmap_id', 'name', 'roadmap_detail_url')
        
    def get_roadmap_detail_url(self, object) -> str:
        http_request = self.context.get('request')
        if http_request:
            return http_request.build_absolute_uri(uri_to_iri(reverse('roadmap-id-review-v1', args=[object.roadmap_id])))
        else:
            return ''

class Roadmap_Full_Serializer(serializers.ModelSerializer):
    '''
    Return Roadmap(s) and related Badge details
    '''

    badges = Roadmap_Badge_Serializer(source='roadmap_badge_set', many=True)

    class Meta:
        model = Roadmap
        fields = ('roadmap_id', 'name', 'graphic', 'executive_summary', 'infrastructure_types', 'integration_coordinators', 'status', 'badges')
        excluce = ()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        badges = representation.get('badges', [])
        # Sort the badges by sequence_no
        sorted_badges = sorted(badges, key=lambda x: x['sequence_no'])
        representation['badges'] = sorted_badges
        return representation


class Resource_Badge_Serializer(serializers.ModelSerializer):
    '''
    Return all fields of an Resource_Badge object, including the badge status. 
    The badges returned are at least planned.
    '''

    status = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()

    class Meta:
        model = Resource_Badge
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


class Resource_Badge_Verification_Serializer(serializers.ModelSerializer):
    '''
    Resource Badge Verification Review Information
    '''

    badge = Badge_Min_Serializer()
    roadmap = Roadmap_Min_Serializer()

    class Meta:
        model = Resource_Badge
        fields = ('info_resourceid', 'badge', 'roadmap', 'id')
        

class Resource_Roadmap_Serializer(serializers.ModelSerializer):
    '''
    Return Resource Roadap details
    '''

    resource_roadmap_id = serializers.SerializerMethodField()
    roadmap_id = serializers.SerializerMethodField()
    roadmap = serializers.SerializerMethodField()

    class Meta:
        model = Resource_Roadmap
        fields = ('resource_roadmap_id', 'info_resourceid', 'roadmap_id', 'roadmap')

    def get_resource_roadmap_id(self, obj) -> str:
        return obj.id
 
    def get_roadmap_id(self, obj) -> str:
        try:
            return obj.roadmap.roadmap_id
        except:
            return None

    def get_roadmap(self, obj) -> Dict[str, Any]:
        serializer = Roadmap_Full_Serializer(obj.roadmap)
        try:
            return serializer.data
        except:
            return None


class Resource_Full_Serializer(serializers.ModelSerializer):
    '''
    Integrating resource CiderInfrastructure, Roadmaps, and Badge information
    '''

    short_name = serializers.SerializerMethodField()
    organization_id = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    organization_url = serializers.SerializerMethodField()
    organization_logo_url = serializers.SerializerMethodField()
    user_guide_url = serializers.SerializerMethodField()
    roadmaps = serializers.SerializerMethodField()

    class Meta:
        model = CiderInfrastructure
        fields = ('info_resourceid', 'cider_resource_id', 'cider_type', 'resource_description',
                    'latest_status', 'short_name', 'resource_descriptive_name',
                    'organization_id', 'organization_name', 'organization_url', 'organization_logo_url',
                    'user_guide_url', 'roadmaps',)
    
    def get_short_name(self, object) -> str:
        try:
            return str(object.other_attributes['short_name']) or None
        except:
            return None

    def get_organization_id(self, obj) -> str:
        try:
            return obj.other_attributes['organizations'][0]['organization_id']
        except:
            return None

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
            my_roadmaps = Resource_Roadmap.objects.filter(info_resourceid__exact=obj.info_resourceid)
            serializer = Resource_Roadmap_Serializer(my_roadmaps, many=True)
        except:
            return None
        return serializer.data

#    def get_badge_status(self, obj) -> Dict[str, Any]:
#        try:
#            my_badges = Resource_Badge.objects.filter(info_resourceid__exact=obj.info_resourceid)
#            badge_status = []
#            for my_badge in my_badges:
#                badge_data = {
#                    'info_resourceid': my_badge.info_resourceid,
#                    'roadmap_id': my_badge.roadmap.roadmap_id,
#                    'badge_id': my_badge.badge.badge_id,
#                    'badge_access_url': my_badge.badge_access_url_or_default,
#                    'badge_access_url_label': my_badge.badge_access_url_label_or_default,
#                    'status': my_badge.status,
#                    'status_updated_by': my_badge.workflow.status_updated_by if my_badge.workflow else None,
#                    'status_updated_at': my_badge.workflow.status_updated_at if my_badge.workflow else None,
#                    'comment': my_badge.workflow.comment if my_badge.workflow else None,
#                    'task_status': my_badge.task_status
#                }
#                badge_status.append(badge_data)
#            return badge_status
#        except Exception as e:
#            return None


class Resource_Badge_Plan_Serializer(serializers.ModelSerializer):
    '''
    Create a new Resource_Badge object.
    '''

    class Meta:
        model = Resource_Badge
        fields = ('badge_access_url', 'badge_access_url_label')

    def create(self, validated_data):
        resource = validated_data.pop('resource', None)
        roadmap = validated_data.pop('roadmap', None)
        badge = validated_data.pop('badge', None)

        if resource is None or badge is None:
            raise serializers.ValidationError("Resource and badge must be provided.")

        resource_badge = Resource_Badge.objects.create(
            info_resourceid=resource.info_resourceid,
            roadmap=roadmap,
            badge=badge,
            **validated_data
        )
        return resource_badge


class Resource_Badge_Workflow_Serializer(serializers.ModelSerializer):
    '''
    Serialize resource badge workflow
    '''
    
    class Meta:
        model = Resource_Badge_Workflow
        fields = '__all__'
        
class Resource_Badge_Task_Workflow_Serializer(serializers.ModelSerializer):
    '''
    Serialize resource badge task workflow
    '''
    
    class Meta:
        model = Resource_Badge_Task_Workflow
        fields = '__all__'

class Resource_Workflow_Post_Serializer(serializers.ModelSerializer):
    '''
    Serialize the body for all Resource Worfklow posts
    '''

    class Meta:
        model = Resource_Badge_Workflow
        fields = ('status_updated_by', 'comment')

class Resource_Enrollments_Serializer(serializers.Serializer):
    '''
    Serialize resource roadmap enrollments body
    '''
    badge_ids = serializers.ListField()

    class Meta:
        fields = ('badge_ids')

class Resource_Enrollments_Response_Serializer(serializers.Serializer):
    '''
    Serialize resource roadmap enrollments response
    '''
    status_code = serializers.CharField()
    message = serializers.CharField()

    class Meta:
        fields = ('status_code', 'message')


#class Resource_Badge_Status_Serializer(serializers.ModelSerializer):
#    '''
#    Return the statuses of all badges (at least planned) associated with a resource.
#    '''
#
#    badge_status = serializers.SerializerMethodField()
#
#    class Meta:
#        model = Resource_Badge
#        fields = ('badge_status')
#
#    def get_badge_status(self, obj):
#        try:
#            badges = obj.resource_badges.all()
#
#            badge_status = []
#            for badge in badges:
#                badge_data = {
#                    'badge_id': badge.badge_id.badge_id,
#                    'badge_access_url': badge.badge_access_url,
#                    'badge_access_url_label': badge.badge_access_url_label,
#                    'status': badge.workflow.status,
#                    'status_updated_by': badge.workflow.status_updated_by if badge.workflow else None,
#                    'status_updated_at': badge.workflow.status_updated_at if badge.workflow else None
#                }
#                badge_status.append(badge_data)
#
#            return badge_status
#        except:
#            return None
