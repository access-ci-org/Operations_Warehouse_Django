from datetime import datetime
from django.urls import reverse
from django.utils.encoding import uri_to_iri
from cider.models import *
from rest_framework import serializers

class CiderInfrastructure_OtherAttrs_Serializer( serializers.ModelSerializer ):
    class Meta:
        model = CiderInfrastructure
        fields = ( 'other_attributes', )

class CiderInfrastructure_ACCESSContacts_Serializer( serializers.ModelSerializer ):
    class Meta:
        model = CiderInfrastructure
        fields = ( 'protected_attributes', )

class CiderInfrastructure_Summary_Serializer(serializers.ModelSerializer):
    short_name = serializers.SerializerMethodField()
    cider_view_url = serializers.SerializerMethodField()
    cider_data_url = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    organization_url = serializers.SerializerMethodField()
    organization_logo_url = serializers.SerializerMethodField()
    fixed_status = serializers.SerializerMethodField()
    
    class Meta:
        model = CiderInfrastructure
        fields = ('cider_resource_id', 'cider_type', 'info_resourceid', 'project_affiliation',
            'short_name', 'resource_descriptive_name', 'resource_description',
            'latest_status', 'latest_status_begin', 'latest_status_end', 'fixed_status',
            'organization_name', 'organization_url', 'organization_logo_url',
            'cider_view_url', 'cider_data_url', 'updated_at')
        
    def get_short_name(self, object) -> str:
        try:
            return str(object.other_attributes['short_name']) or None
        except:
            return None
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
    def get_cider_view_url(self, object) -> str:
        try:
            return object.other_attributes['public_url']
        except:
            return None
    def get_cider_data_url(self, object) -> str:
        http_request = self.context.get('request')
        if http_request:
            return http_request.build_absolute_uri(uri_to_iri(reverse('cider-detail-v1-id', args=[object.cider_resource_id])))
        else:
            return ''

    def get_fixed_status(self, object) -> str:
        if object.latest_status:
            return object.latest_status
        # Handle the common retired case, and other cases, where there is no latest status
        today_str = datetime.strftime(datetime.now(), '%Y-%m-%d')
        try:
            prod_start = object.resource_status.get('production_begin_date')
            prod_end = object.resource_status.get('production_end_date')
        except:
            prod_start = ''
            prod_end = ''
        if not prod_start or prod_start >= today_str:
            fixed_status = 'coming_soon'
        elif today_str > prod_end:
            fixed_status = 'decommissioned'
        else:
            fixed_status = ''
        return fixed_status

class CiderInfrastructure_Summary_v2_Serializer(serializers.ModelSerializer):
    short_name = serializers.SerializerMethodField()
    cider_view_url = serializers.SerializerMethodField()
    cider_data_url = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    organization_url = serializers.SerializerMethodField()
    organization_logo_url = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    features_list = serializers.SerializerMethodField()
    user_guide_url = serializers.SerializerMethodField()
# Just Online Service
    primary_service_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CiderInfrastructure
        fields = ('cider_resource_id', 'cider_type', 'info_resourceid', 'project_affiliation',
            'short_name', 'resource_descriptive_name', 'resource_description',
            'recommended_use', 'access_description',
            'latest_status', 'latest_status_begin', 'latest_status_end',
            'organization_name', 'organization_url', 'organization_logo_url', 'latitude', 'longitude',
            'features', 'features_list', 'user_guide_url',
            'cider_view_url', 'cider_data_url', 'updated_at',
            'primary_service_url')
        
    def get_short_name(self, object) -> str:
        try:
            return str(object.other_attributes['short_name']) or None
        except:
            return None
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
    def get_user_guide_url(self, object) -> str:
        try:
            return object.other_attributes['user_guide_url']
        except:
            return None
    def get_latitude(self, object) -> float:
        try:
            return object.other_attributes['latitude']
        except:
            return None
    def get_longitude(self, object) -> float:
        try:
            return object.other_attributes['longitude']
        except:
            return None
    def get_features(self, object) -> dict:
        try:
            return object.other_attributes['features']
        except:
            return None
    def get_features_list(self, object) -> dict:
        try:
            features_list = []
            for item in object.other_attributes['features']:
#                features_list.append('{}:{} ({})'.format(item['feature_category'], item['name'], item['description']))
                features_list.append(item['description'])
            return features_list
        except:
            return None
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
# Just Online Service
    def get_primary_service_url(self, object) -> str:
        try:
            return object.other_attributes['primary_service_url']
        except:
            return None

class CiderInfrastructure_Summary_v2_Gateway_Serializer(serializers.ModelSerializer):
    short_name = serializers.SerializerMethodField()
    cider_view_url = serializers.SerializerMethodField()
    cider_data_url = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    organization_url = serializers.SerializerMethodField()
    organization_logo_url = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    features_list = serializers.SerializerMethodField()
    user_guide_url = serializers.SerializerMethodField()
# Just Science Gateway
    primary_service_url = serializers.SerializerMethodField()
    sgx3_url = serializers.SerializerMethodField()
    shortname = serializers.SerializerMethodField()
    long_description = serializers.SerializerMethodField()
    allocated_grant_number = serializers.SerializerMethodField()
    requested_usernames = serializers.SerializerMethodField()

    class Meta:
        model = CiderInfrastructure
        fields = ('cider_resource_id', 'cider_type', 'info_resourceid', 'project_affiliation',
            'short_name', 'resource_descriptive_name', 'resource_description',
            'recommended_use', 'access_description',
            'latest_status', 'latest_status_begin', 'latest_status_end',
            'organization_name', 'organization_url', 'organization_logo_url', 'latitude', 'longitude',
            'features', 'features_list', 'user_guide_url',
            'cider_view_url', 'cider_data_url', 'updated_at',
            'primary_service_url', 'sgx3_url', 'shortname', 'long_description', 'allocated_grant_number', 'requested_usernames')
        
    def get_short_name(self, object) -> str:
        try:
            return str(object.other_attributes['short_name']) or None
        except:
            return None
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
    def get_user_guide_url(self, object) -> str:
        try:
            return object.other_attributes['user_guide_url']
        except:
            return None
    def get_latitude(self, object) -> float:
        try:
            return object.other_attributes['latitude']
        except:
            return None
    def get_longitude(self, object) -> float:
        try:
            return object.other_attributes['longitude']
        except:
            return None
    def get_features(self, object) -> dict:
        try:
            return object.other_attributes['features']
        except:
            return None
    def get_features_list(self, object) -> dict:
        try:
            features_list = []
            for item in object.other_attributes['features']:
#                features_list.append('{}:{} ({})'.format(item['feature_category'], item['name'], item['description']))
                features_list.append(item['description'])
            return features_list
        except:
            return None
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
# Just Science Gateway
    def get_primary_service_url(self, object) -> str:
        try:
            return str(object.other_attributes['url_1']) or None
        except:
            return None

    def get_sgx3_url(self, object) -> str:
        try:
            return str(object.other_attributes['url_2']) or None
        except:
            return None
# Retire someday as replaced by get_short_name on 2025-04-29
    def get_shortname(self, object) -> str:
        try:
            return str(object.other_attributes['short_name']) or None
        except:
            return None
    def get_long_description(self, object) -> str:
        try:
            return str(object.other_attributes['long_description']) or None
        except:
            return None
    def get_allocated_grant_number(self, object) -> str:
        try:
            return str(object.other_attributes['access_allocations_grant_number']) or None
        except:
            return None
    def get_requested_usernames(self, object) -> str:
        try:
            return str(object.other_attributes['requested_usernames']) or None
        except:
            return None

class CiderInfrastructure_Detail_Serializer(serializers.ModelSerializer):
#    cider_type = serializers.SerializerMethodField()
    cider_view_url = serializers.SerializerMethodField()
    _result_item_url = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    organization_url = serializers.SerializerMethodField()
    organization_logo_url = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    groups = serializers.SerializerMethodField()
    compute = serializers.SerializerMethodField()
    storage = serializers.SerializerMethodField()
    gateway = serializers.SerializerMethodField()

    class Meta:
        model = CiderInfrastructure
        exclude = ('parent_resource', 'recommended_use', 'access_description', 'provider_level', 'other_attributes', 'protected_attributes')
        
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
    def get_features(self, object) -> dict:
        try:    # Gracefully ignore missing compute
            return object.other_attributes['features']
        except:
            return None
    def get_groups(self, object) -> dict:
        try:    # Gracefully ignore missing compute
            return object.other_attributes['group_ids']
        except:
            return None
    def get_compute(self, object) -> dict:
        if object.cider_type == 'Compute':
            try:    # Gracefully ignore missing compute
                return CiderInfrastructure_Compute_Detail_Serializer(object).data
            except:
                pass
        return None
    def get_storage(self, object) -> dict:
        if object.cider_type == 'Storage':
            try:
                return CiderInfrastructure_Storage_Detail_Serializer(object).data
            except:
                pass
        return None
    def get_gateway(self, object) -> dict:
        if object.cider_type == 'Science Gateway':
            try:
                return CiderInfrastructure_Gateway_Detail_Serializer(object).data
            except:
                pass
        return None

class CiderInfrastructure_Compute_Detail_Serializer(serializers.ModelSerializer):
    access_description = serializers.SerializerMethodField()
    batch_system = serializers.SerializerMethodField()
    cpu_count_per_node = serializers.SerializerMethodField()
    cpu_speed_ghz = serializers.SerializerMethodField()
    cpu_type = serializers.SerializerMethodField()
    gpu_description = serializers.SerializerMethodField()
    interconnect = serializers.SerializerMethodField()
    job_manager = serializers.SerializerMethodField()
    local_storage_per_node_gb = serializers.SerializerMethodField()
    machine_type = serializers.SerializerMethodField()
    manufacturer = serializers.SerializerMethodField()
    memory_per_cpu_gb = serializers.SerializerMethodField()
    node_count = serializers.SerializerMethodField()
    operating_system = serializers.SerializerMethodField()
    platform_name = serializers.SerializerMethodField()
    sensitive_data_support_description = serializers.SerializerMethodField()
    storage_network = serializers.SerializerMethodField()
    supports_senstitive_data = serializers.SerializerMethodField()
    user_guide_url = serializers.SerializerMethodField()
    xsedenet_participation = serializers.SerializerMethodField()

    class Meta:
        model = CiderInfrastructure
        fields = ('cider_resource_id', 'recommended_use', 'access_description', 'user_guide_url', 'cpu_type', 'operating_system', 'gpu_description', 'job_manager', 'batch_system', 'interconnect', 'storage_network', 'machine_type', 'manufacturer', 'cpu_speed_ghz', 'platform_name', 'memory_per_cpu_gb', 'cpu_count_per_node', 'xsedenet_participation', 'node_count', 'supports_senstitive_data', 'sensitive_data_support_description', 'local_storage_per_node_gb')

    def get_access_description(self, object) -> str:
        try:
            return str(object.access_description) or None
        except:
            return None
    def get_batch_system(self, object) -> str:
        try:
            return str(object.other_attributes['batch_system']) or None
        except:
            return None
    def get_cpu_count_per_node(self, object) -> int:
        try:
            return object.other_attributes['cpu_count_per_node']
        except:
            return None
    def get_cpu_speed_ghz(self, object) -> int:
        try:
            return object.other_attributes['cpu_speed_ghz']
        except:
            return None
    def get_cpu_type(self, object) -> str:
        try:
            return str(object.other_attributes['cpu_type']) or None
        except:
            return None
    def get_gpu_description(self, object) -> str:
        try:
            return str(object.other_attributes['gpu_description']) or None
        except:
            return None
    def get_interconnect(self, object) -> str:
        try:
            return str(object.other_attributes['interconnect']) or None
        except:
            return None
    def get_job_manager(self, object) -> str:
        try:
            return str(object.other_attributes['job_manager']) or None
        except:
            return None
    def get_local_storage_per_node_gb(self, object) -> int:
        try:
            return object.other_attributes['local_storage_per_node_gb']
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
    def get_memory_per_cpu_gb(self, object) -> int:
        try:
            return object.other_attributes['memory_per_cpu_gb']
        except:
            return None
    def get_node_count(self, object) -> int:
        try:
            return object.other_attributes['node_count']
        except:
            return None
    def get_operating_system(self, object) -> str:
        try:
            return str(object.other_attributes['operating_system']) or None
        except:
            return None
    def get_platform_name(self, object) -> str:
        try:
            return str(object.other_attributes['platform_name']) or None
        except:
            return None
    def get_sensitive_data_support_description(self, object) -> str:
        try:
            return str(object.other_attributes['sensitive_data_support_description']) or None
        except:
            return None
    def get_storage_network(self, object) -> str:
        try:
            return str(object.other_attributes['storage_network']) or None
        except:
            return None
    def get_supports_senstitive_data(self, object) -> bool:
        try:
            return object.other_attributes['supports_senstitive_data']
        except:
            return None
    def get_user_guide_url(self, object) -> str:
        try:
            return str(object.other_attributes['user_guide_url']) or None
        except:
            return None
    def get_xsedenet_participation(self, object) -> str:
        try:
            return object.other_attributes['xsedenet_participation']
        except:
            return None

class CiderInfrastructure_Storage_Detail_Serializer(serializers.ModelSerializer):
    user_guide_url = serializers.SerializerMethodField()
    databases = serializers.SerializerMethodField()
    file_space_tb = serializers.SerializerMethodField()
    specifications = serializers.SerializerMethodField()
    supports_sensitive_data = serializers.SerializerMethodField()
    sensitive_data_support_description = serializers.SerializerMethodField()
    
    class Meta:
        model = CiderInfrastructure
        fields = ('cider_resource_id', 'recommended_use', 'user_guide_url', 'databases', 'file_space_tb', 'specifications', 'supports_sensitive_data', 'sensitive_data_support_description')

    def get_user_guide_url(self, object) -> str:
        try:
            return str(object.other_attributes['user_guide_url']) or None
        except:
            return None
    def get_databases(self, object) -> str:
        try:
            return object.other_attributes['databases']
        except:
            return None
    def get_file_space_tb(self, object) -> int:
        try:
            return object.other_attributes['file_space_tb']
        except:
            return None
    def get_specifications(self, object) -> str:
        try:
            return object.other_attributes['specifications']
        except:
            return None
    def get_supports_sensitive_data(self, object) -> bool:
        try:
            return object.other_attributes['supports_sensitive_data']
        except:
            return None
    def get_sensitive_data_support_description(self, object) -> str:
        try:
            return object.other_attributes['sensitive_data_support_description']
        except:
            return None

class CiderInfrastructure_Gateway_Detail_Serializer(serializers.ModelSerializer):
    primary_service_url = serializers.SerializerMethodField()
    sgx3_url = serializers.SerializerMethodField()
    shortname = serializers.SerializerMethodField()
    long_description = serializers.SerializerMethodField()
    allocated_grant_number = serializers.SerializerMethodField()
    requested_usernames = serializers.SerializerMethodField()
    
    class Meta:
        model = CiderInfrastructure
        fields = ('primary_service_url', 'sgx3_url', 'shortname', 'user_guide_url', 'allocated_grant_number', 'requested_usernames')

    def get_primary_service_url(self, object) -> str:
        try:
            return str(object.other_attributes['url_1']) or None
        except:
            return None
    def get_sgx3_url(self, object) -> str:
        try:
            return str(object.other_attributes['url_1']) or None
        except:
            return None
    def get_shortname(self, object) -> str:
        try:
            return str(object.other_attributes['short_name']) or None
        except:
            return None
    def get_long_description(self, object) -> str:
        try:
            return str(object.other_attributes['long_description']) or None
        except:
            return None
    def get_allocated_grant_number(self, object) -> str:
        try:
            return str(object.other_attributes['access_allocations_grant_number']) or None
        except:
            return None
    def get_requested_usernames(self, object) -> str:
        try:
            return str(object.other_attributes['requested_usernames']) or None
        except:
            return None

class CiderFeatures_Serializer(serializers.ModelSerializer):
    class Meta:
        model = CiderFeatures
        fields = ('__all__')

class CiderGroups_Serializer(serializers.ModelSerializer):
    class Meta:
        model = CiderGroups
        fields = ('__all__')

class CiderOrganizations_Serializer(serializers.ModelSerializer):
    class Meta:
        model = CiderOrganizations
        fields = ('__all__')

class CiderACCESSActiveGroups_v1_List_Serializer(serializers.ModelSerializer):
    rollup_info_resourceids = serializers.SerializerMethodField()
    rollup_feature_ids = serializers.SerializerMethodField()
    rollup_organization_ids = serializers.SerializerMethodField()
    class Meta:
        model = CiderGroups
        fields = ('group_id', 'info_groupid', 'group_descriptive_name', 'group_description',
            'group_logo_url', 'group_types', 'other_attributes',
            'rollup_info_resourceids', 'rollup_feature_ids', 'rollup_organization_ids')

    def get_rollup_info_resourceids(self, object) -> list[str]:
        try:
            return self.context['groups_extra'][object.info_groupid]['rollup_active_info_resourceids']
        except:
            return([])
    def get_rollup_feature_ids(self, object) -> list[int]:
        try:
            return self.context['groups_extra'][object.info_groupid]['rollup_feature_ids']
        except:
            return([])
    def get_rollup_organization_ids(self, object) -> list[str]:
        try:
            return self.context['groups_extra'][object.info_groupid]['rollup_org_ids']
        except:
            return([])
