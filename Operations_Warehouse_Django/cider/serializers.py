from django.urls import reverse
from django.utils.encoding import uri_to_iri
from cider.models import *
from rest_framework import serializers

class CiderInfrastructure_Serializer(serializers.ModelSerializer):
    cider_view_url = serializers.SerializerMethodField()
    _result_item_url = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    organization_url = serializers.SerializerMethodField()
    organization_logo_url = serializers.SerializerMethodField()
    class Meta:
        model = CiderInfrastructure
        fields = ('__all__')
    def get_cider_view_url(self, CiderInfrastructure):
        try:
            return CiderInfrastructure.other_attributes['public_url']
        except:
            return None
    def get__result_item_url(self, CiderInfrastructure):
        http_request = self.context.get('request')
        if http_request:
            return http_request.build_absolute_uri(uri_to_iri(reverse('cider-detail-v1-id', args=[CiderInfrastructure.cider_resource_id])))
        else:
            return ''
    def get_organization_name(self, CiderInfrastructure):
        try:
            return CiderInfrastructure.other_attributes['organizations'][0]['organization_name']
        except:
            return None
    def get_organization_url(self, CiderInfrastructure):
        try:
            return CiderInfrastructure.other_attributes['organizations'][0]['organization_url']
        except:
            return None
    def get_organization_logo_url(self, CiderInfrastructure):
        try:
            return CiderInfrastructure.other_attributes['organizations'][0]['organization_logo_url']
        except:
            return None
