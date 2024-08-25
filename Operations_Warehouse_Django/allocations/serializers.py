from rest_framework import serializers
from .models import *
from django.utils.encoding import uri_to_iri
from django.urls import reverse
import copy

class Allocations_fos_Serializer(serializers.ModelSerializer):
    class Meta:
        model = FieldOfScience
        fields = ('__all__')

class Allocations_fos_DetailURL_Serializer(serializers.ModelSerializer):
    DetailURL = serializers.SerializerMethodField()
    
    def get_DetailURL(self, FieldOfScience) -> str:
        http_request = self.context.get('request')
        if http_request:
            return http_request.build_absolute_uri(uri_to_iri(reverse('accessdb-fos-detail', args=[FieldOfScience.field_of_science_id])))
        else:
            return ''

    class Meta:
        model = FieldOfScience
        fields = copy.copy([f.name for f in FieldOfScience._meta.get_fields(include_parents=False)])
        fields.append('DetailURL')

