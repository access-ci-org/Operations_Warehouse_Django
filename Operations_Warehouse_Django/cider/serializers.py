from cider.models import *
from rest_framework import serializers

class CiderInfrastructure_Serializer(serializers.ModelSerializer):
    public_url = serializers.SerializerMethodField()
    organization_name = serializers.SerializerMethodField()
    organization_url = serializers.SerializerMethodField()
    organization_logo_url = serializers.SerializerMethodField()
    class Meta:
        model = CiderInfrastructure
        fields = ('__all__')
    def get_public_url(self, CiderInfrastructure):
        try:
            return CiderInfrastructure.other_attributes['public_url']
        except:
            return None
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
