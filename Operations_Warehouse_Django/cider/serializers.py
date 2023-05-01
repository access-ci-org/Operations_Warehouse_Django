from django.urls import reverse
from django.utils.encoding import uri_to_iri
from cider.models import *
from rest_framework import serializers

class CiderInfrastructure_Summary_Serializer(serializers.ModelSerializer):
    cider_view_url = serializers.SerializerMethodField()
    cider_data_url = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    organization_url = serializers.SerializerMethodField()
    organization_logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CiderInfrastructure
        fields = ('cider_resource_id', 'cider_view_url', 'cider_data_url', 'organization_name', 'organization_url', 'organization_logo_url', 'cider_type', 'info_resourceid', 'resource_descriptive_name', 'resource_description', 'latest_status', 'latest_status_begin', 'latest_status_end', 'project_affiliation', 'updated_at')
        
    def get_cider_view_url(self, CiderInfrastructure) -> str:
        try:
            return CiderInfrastructure.other_attributes['public_url']
        except:
            return None
    def get_cider_data_url(self, object) -> str:
        http_request = self.context.get('request')
        if http_request:
            return http_request.build_absolute_uri(uri_to_iri(reverse('cider-detail-v1-id', args=[object.cider_resource_id])))
        else:
            return ''
    def get_organization_name(self, object) -> str:
        try:
            return object.other_attributes['organizations'][0]['organization_name']
        except:
            return None
    def get_organization_url(self, object) -> str:
        try:
            return object.other_attributes['organizations'][0]['organization_url']
        except:
            return None
    def get_organization_logo_url(self, object) -> str:
        try:
            return object.other_attributes['organizations'][0]['organization_logo_url']
        except:
            return None

class CiderInfrastructure_Detail_Serializer(serializers.ModelSerializer):
    cider_type = serializers.SerializerMethodField()
    cider_view_url = serializers.SerializerMethodField()
    _result_item_url = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    organization_url = serializers.SerializerMethodField()
    organization_logo_url = serializers.SerializerMethodField()
    compute = serializers.SerializerMethodField()
    
    class Meta:
        model = CiderInfrastructure
        exclude = ('parent_resource', 'recommended_use', 'access_description', 'provider_level', 'other_attributes')
        
    def get_cider_type(self, object) -> str:
        return('compute')
        
    def get_cider_view_url(self, object) -> str:
        try:
            return str(object.other_attributes['public_url']) or None
        except:
            return None
    def get__result_item_url(self, object) -> str:
        http_request = self.context.get('request')
        if http_request:
            return http_request.build_absolute_uri(uri_to_iri(reverse('cider-detail-v1-id', args=[object.cider_resource_id])))
        else:
            return ''
    def get_organization_name(self, object) -> str:
        try:
            return object.other_attributes['organizations'][0]['organization_name']
        except:
            return None
    def get_organization_url(self, object) -> str:
        try:
            return str(object.other_attributes['organizations'][0]['organization_url']) or None
        except:
            return None
    def get_organization_logo_url(self, object) -> str:
        try:
            return str(object.other_attributes['organizations'][0]['organization_logo_url']) or None
        except:
            return None
    def get_compute(self, object) -> dict:
        try:    # Gracefully ignore missing compute
            compute = CiderInfrastructure.objects.get(parent_resource=object.cider_resource_id, cider_type='compute')
        except:
            return None
        if compute:
            return CiderInfrastructure_Compute_Serializer(compute).data
        else:
            return None

class CiderInfrastructure_Compute_Detail_Serializer(serializers.ModelSerializer):
    access_description = serializers.SerializerMethodField()
    user_guide_url = serializers.SerializerMethodField()
    cpu_type = serializers.SerializerMethodField()
    operating_system = serializers.SerializerMethodField()
    gpu_description = serializers.SerializerMethodField()
    job_manager = serializers.SerializerMethodField()
    batch_system = serializers.SerializerMethodField()
    interconnect = serializers.SerializerMethodField()
    storage_network = serializers.SerializerMethodField()
    machine_type = serializers.SerializerMethodField()
    manufacturer = serializers.SerializerMethodField()
    cpu_speed_ghz = serializers.SerializerMethodField()
    platform_name = serializers.SerializerMethodField()
    memory_per_cpu_gb = serializers.SerializerMethodField()
    cpu_count_per_node = serializers.SerializerMethodField()
    xsedenet_participation = serializers.SerializerMethodField()
    supports_senstitive_data = serializers.SerializerMethodField()
    sensitive_data_support_description = serializers.SerializerMethodField()
    local_storage_per_node_gb = serializers.SerializerMethodField()
    
    class Meta:
        model = CiderInfrastructure
        fields = ('cider_resource_id', 'recommended_use', 'access_description', 'user_guide_url', 'cpu_type', 'operating_system', 'gpu_description', 'job_manager', 'batch_system', 'interconnect', 'storage_network', 'machine_type', 'manufacturer', 'cpu_speed_ghz', 'platform_name', 'memory_per_cpu_gb', 'cpu_count_per_node', 'xsedenet_participation', 'supports_senstitive_data', 'sensitive_data_support_description', 'local_storage_per_node_gb')

    def get_access_description(self, object) -> str:
        try:
            return str(object.access_description) or None
        except:
            return None

    def get_user_guide_url(self, object) -> str:
        try:
            return str(object.other_attributes['user_guide_url']) or None
        except:
            return None
            
    def get_cpu_type(self, object) -> str:
        try:
            return str(object.other_attributes['cpu_type']) or None
        except:
            return None
            
    def get_operating_system(self, object) -> str:
        try:
            return str(object.other_attributes['operating_system']) or None
        except:
            return None

    def get_gpu_description(self, object) -> str:
        try:
            return str(object.other_attributes['gpu_description']) or None
        except:
            return None
            
    def get_job_manager(self, object) -> str:
        try:
            return str(object.other_attributes['job_manager']) or None
        except:
            return None
            
    def get_batch_system(self, object) -> str:
        try:
            return str(object.other_attributes['batch_system']) or None
        except:
            return None
            
    def get_interconnect(self, object) -> str:
        try:
            return str(object.other_attributes['interconnect']) or None
        except:
            return None
            
    def get_storage_network(self, object) -> str:
        try:
            return str(object.other_attributes['storage_network']) or None
        except:
            return None
            
    def get_machine_type(self, object) -> str:
        try:
            return str(object.other_attributes['machine_type']) or None
        except:
            return None
            
    def get_manufacturer(self, object) -> str:
        try:
            return str(object.other_attributes['manufacturer']) or None
        except:
            return None
            
    def get_cpu_speed_ghz(self, object) -> int:
        try:
            return object.other_attributes['cpu_speed_ghz']
        except:
            return None
            
    def get_platform_name(self, object) -> str:
        try:
            return str(object.other_attributes['platform_name']) or None
        except:
            return None
            
    def get_memory_per_cpu_gb(self, object) -> int:
        try:
            return object.other_attributes['memory_per_cpu_gb']
        except:
            return None
            
    def get_cpu_count_per_node(self, object) -> int:
        try:
            return object.other_attributes['cpu_count_per_node']
        except:
            return None
            
    def get_xsedenet_participation(self, object) -> str:
        try:
            return object.other_attributes['xsedenet_participation']
        except:
            return None
            
    def get_supports_senstitive_data(self, object) -> bool:
        try:
            return object.other_attributes['supports_senstitive_data']
        except:
            return None
            
    def get_sensitive_data_support_description(self, object) -> str:
        try:
            return str(object.other_attributes['sensitive_data_support_description']) or None
        except:
            return None
            
    def get_local_storage_per_node_gb(self, object) -> int:
        try:
            return object.other_attributes['local_storage_per_node_gb']
        except:
            return None
