import copy
from glue2.models import *
from rest_framework import serializers

class JSON_Serializer(serializers.Serializer):
    json_data = serializers.JSONField()
    
class AdminDomain_Serializer(serializers.ModelSerializer):
    class Meta:
        model = AdminDomain
        fields = ('ID', 'Name', 'CreationTime', 'Validity' , 'EntityJSON', \
                  'Description', 'WWW', 'Distributed', 'Owner')

class UserDomain_Serializer(serializers.ModelSerializer):
    class Meta:
        model = UserDomain
        fields = ('ID', 'Name', 'CreationTime', 'Validity' , 'EntityJSON', \
                  'Description', 'WWW', 'Level', 'UserManager', 'Member')

class AccessPolicy_Serializer(serializers.ModelSerializer):
    class Meta:
        model = AccessPolicy
        fields = ('ID', 'Name', 'CreationTime', 'Validity' , 'EntityJSON', \
                  'Scheme', 'Rule')

class Contact_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('ID', 'Name', 'CreationTime', 'Validity' , 'EntityJSON', \
                  'Detail', 'Type')

class Location_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('ID', 'Name', 'CreationTime', 'Validity' , 'EntityJSON')
#
class ApplicationEnvironment_Serializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationEnvironment
        fields = ('ID', 'ResourceID', 'Name', 'CreationTime', 'Validity', 'EntityJSON', \
                  'Description', 'AppName', 'AppVersion')

class ApplicationHandle_Serializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationHandle
        fields = ('ID', 'ResourceID', 'Name', 'CreationTime', 'Validity', 'EntityJSON', \
                  'ApplicationEnvironment', 'Type', 'Value')

class AbstractService_Serializer(serializers.ModelSerializer):
    class Meta:
        model = AbstractService
        fields = ('ID', 'ResourceID', 'Name', 'CreationTime', 'Validity', 'EntityJSON', \
                  'ServiceType', 'Type', 'QualityLevel')

class Endpoint_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Endpoint
        fields = ('ID', 'ResourceID', 'Name', 'CreationTime', 'Validity', 'EntityJSON', \
                  'AbstractService', 'HealthState', 'ServingState', 'URL', \
                  'QualityLevel', 'InterfaceVersion', 'InterfaceName')

class EndpointServices_Serializer(serializers.ModelSerializer):
    ServiceType = serializers.CharField(source='AbstractService.ServiceType')
    class Meta:
        model = Endpoint
        fields = ('ResourceID', 'InterfaceName', 'InterfaceVersion', 'URL',
                  'QualityLevel', 'ServingState', 'HealthState', 'ServiceType',
                  'CreationTime', 'ID')

# Same as EndpointServices_Serializer but adds AbstractService Extension SupportContact
class EndpointServices_Support_Serializer(serializers.ModelSerializer):
    ServiceType = serializers.CharField(source='AbstractService.ServiceType')
    SupportContact = serializers.SerializerMethodField('get_supportcontact')
    class Meta:
        model = Endpoint
        fields = ('ResourceID', 'InterfaceName', 'InterfaceVersion', 'URL',
                  'QualityLevel', 'ServingState', 'HealthState', 'ServiceType',
                  'CreationTime', 'ID', 'SupportContact')
    def get_supportcontact(self, Endpoint) -> str:
        try:
            return Endpoint.AbstractService.EntityJSON['Extension']['SupportContact']
        except:
            return []

class ComputingManager_Serializer(serializers.ModelSerializer):
    class Meta:
        model = ComputingManager
        fields = ('ID', 'ResourceID', 'Name', 'CreationTime', 'Validity', 'EntityJSON')

class ExecutionEnvironment_Serializer(serializers.ModelSerializer):
    class Meta:
        model = ExecutionEnvironment
        fields = ('ID', 'ResourceID', 'Name', 'CreationTime', 'Validity', 'EntityJSON')

class ComputingShare_Serializer(serializers.ModelSerializer):
    class Meta:
        model = ComputingShare
        fields = ('ID', 'ResourceID', 'Name', 'CreationTime', 'Validity', 'EntityJSON')

class ComputingQueue_Serializer(serializers.ModelSerializer):
    class Meta:
        model = ComputingQueue
        fields = ('ID', 'ResourceID', 'Name', 'CreationTime', 'Validity', 'EntityJSON')

class ComputingQueue_Expand_Serializer(serializers.ModelSerializer):
    JobQueue = serializers.SerializerMethodField()
    def get_JobQueue(self, ComputingQueue) -> str:
#        try:
#            sort_by = self.context.get('sort_by', None)
#            if sort_by:
#                jobsort = {}
#                for key in ComputingQueue.EntityJSON:
#                    jobin = ComputingQueue.EntityJSON[key]
#                    try:
#                        if sort_by in ('RequestedTotalWallTime', 'RequestedSlots'):
#                            prefix = '{:d030d}'.format(jobin[sort_by])
#                        elif sort_by in ('SubmissionTime', 'StartTime'):
#                            prefix = '{:%Y/%m/%d %H:%M:%S %Z}'.format(jobin[sort_by])
#                        else:
#                            prefix = jobin[sort_by]
#                    except:
#                        prefix = jobin[sort_by]
#                    jobsort[prefix + ':' + jobin['ID']] = jobin
#            else:
#                jobsort = ComputingQueue.EntityJSON
#        except Exception as e:
#            jobsort = ComputingQueue.EntityJSON
        response = []
#        for key in sorted(jobsort):
        for key in ComputingQueue.EntityJSON:
            if key == 'Extension':
                continue
            jobin = ComputingQueue.EntityJSON[key]
            jobout = {'ID': jobin['LocalIDFromManager']}
            for s in jobin['State']:
                if s.startswith('ipf:'):
                    jobout['State'] = s[4:]
            jobout['Name'] = jobin['Name']
            jobout['LocalOwner'] = jobin['LocalOwner']
            jobout['Queue'] = jobin['Queue']
            jobout['SubmissionTime'] = jobin['SubmissionTime']
            jobout['RequestedSlots'] = jobin['RequestedSlots']
            jobout['RequestedTotalWallTime'] = jobin['RequestedTotalWallTime']
            jobout['StartTime'] = jobin.get('StartTime', None)
            response.append(jobout)
        return response
    class Meta:
        model = ComputingQueue
        fields = ('ResourceID', 'Name', 'CreationTime', 'Validity', 'ID', 'JobQueue')

class ComputingActivity_Serializer(serializers.ModelSerializer):
    class Meta:
        model = ComputingActivity
        fields = ('ID', 'ResourceID', 'Name', 'CreationTime', 'Validity', 'EntityJSON')

class ComputingActivity_Expand_Serializer(serializers.ModelSerializer):
    DetailURL = serializers.SerializerMethodField()
    StandardState = serializers.SerializerMethodField()
    def get_DetailURL(self, ComputingActivity) -> str:
        http_request = self.context.get('request')
        if http_request:
            return http_request.build_absolute_uri(uri_to_iri(reverse('jobs-detail', args=[ComputingActivity.ID])))
        else:
            return ''
    def get_StandardState(self, ComputingActivity) -> str:
        for s in ComputingActivity.EntityJSON.get('State'):
            if s.startswith('ipf:'):
                return s[4:]
        return ''
    class Meta:
        model = ComputingActivity
        fields = copy.copy([f.name for f in ComputingActivity._meta.get_fields(include_parents=False)])
        fields.append('DetailURL')
        fields.append('StandardState')

class ComputingManagerAcceleratorInfo_Serializer(serializers.ModelSerializer):
    class Meta:
        model = ComputingManagerAcceleratorInfo
        fields = ('ID', 'ResourceID', 'Name', 'CreationTime', 'Validity', 'EntityJSON')

class ComputingManagerAcceleratorInfo_Serializer(serializers.ModelSerializer):
    class Meta:
        model = ComputingManagerAcceleratorInfo
        fields = ('ID', 'ResourceID', 'Name', 'CreationTime', 'Validity', 'EntityJSON')

class ComputingShareAcceleratorInfo_Serializer(serializers.ModelSerializer):
    class Meta:
        model = ComputingShareAcceleratorInfo
        fields = ('ID', 'ResourceID', 'Name', 'CreationTime', 'Validity', 'EntityJSON')

class AcceleratorEnvironment_Serializer(serializers.ModelSerializer):
    class Meta:
        model = AcceleratorEnvironment
        fields = ('ID', 'ResourceID', 'Name', 'CreationTime', 'Validity', 'EntityJSON', \
                  'Type')

class EntityHistory_Serializer(serializers.ModelSerializer):
    class Meta:
        model = EntityHistory
        fields = ('ID', 'DocumentType', 'ResourceID', 'ReceivedTime', 'EntityJSON')

class EntityHistory_Usage_Serializer(serializers.ModelSerializer):
    class Meta:
        model = EntityHistory
        fields = ('DocumentType', 'ResourceID', 'ReceivedTime')
