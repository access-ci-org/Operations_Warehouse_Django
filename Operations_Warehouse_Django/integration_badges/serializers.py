from django.urls import reverse
from django.utils.encoding import uri_to_iri
from integration_badges.models import *
from rest_framework import serializers



class Integration_Badge_Serializer(serializers.ModelSerializer):
    #    badges = serializers.SerializerMethodField()

    #badges = serializers.RelatedField(many=True)

    class Meta:
        model = Integration_Badge
        fields = ('badge_id', 'name')

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
