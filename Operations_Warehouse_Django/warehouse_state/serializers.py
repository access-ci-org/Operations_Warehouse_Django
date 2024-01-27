from rest_framework import serializers
from .models import *
from django.utils.encoding import iri_to_uri
from django.utils.html import smart_urlquote
from django.urls import reverse
import copy
import json

class ProcessingStatus_DbSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessingStatus
        fields = copy.copy([f.name for f in ProcessingStatus._meta.get_fields(include_parents=False)])

class ProcessingStatus_DetailURL_DbSerializer(serializers.ModelSerializer):
    ProcessingStart = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S %Z')
    ProcessingEnd = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S %Z')
    DetailURL = serializers.SerializerMethodField()
    HistoryURL = serializers.SerializerMethodField()

    def get_DetailURL(self, ProcessingStatus) -> str:
        http_request = self.context.get('request')
        if http_request:
            return http_request.build_absolute_uri(iri_to_uri(reverse('processingrecord-detail', kwargs={'id': ProcessingStatus.ID} )))
        else:
            return ''
    def get_HistoryURL(self, ProcessingStatus) -> str:
        # Not sure this works. Requires ProcessingMessage to be serialized Dict
        #       which we just started to do
        # Debug this once we have ProcessingMessages that are serialized Dict
        http_request = self.context.get('request')
        if not http_request:
            return ''
        try:
            message_json = json.loads(ProcessingStatus.ProcessingMessage)
            if message_json['Label'].startswith('EntityHistory.ID='):
                historyid = message_json['Label'].split('=')[1]
                return http_request.build_absolute_uri(iri_to_uri(reverse('entityhistory-detail', kwargs={'id': smart_urlquote(historyid)} )))
        except:
            return ''
    class Meta:
        model = ProcessingStatus
        fields = copy.copy([f.name for f in ProcessingStatus._meta.get_fields(include_parents=False)])
        fields.extend(['DetailURL', 'HistoryURL'])

class PublisherInfo_DbSerializer(serializers.ModelSerializer):
    CreationTime = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S %Z')
    class Meta:
        model = PublisherInfo
        fields = copy.copy([f.name for f in PublisherInfo._meta.get_fields(include_parents=False)])

class PublisherInfo_DetailURL_DbSerializer(serializers.ModelSerializer):
    CreationTime = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S %Z')
    DetailURL = serializers.SerializerMethodField()

    def get_DetailURL(self, PublisherInfo) -> str:
        http_request = self.context.get('request')
        if http_request:
            return http_request.build_absolute_uri(iri_to_uri(reverse('publisherinfo-detail', args=[smart_urlquote(PublisherInfo.ID)] )))
        else:
            return ''
    class Meta:
        model = PublisherInfo
        fields = copy.copy([f.name for f in PublisherInfo._meta.get_fields(include_parents=False)])
        fields.append('DetailURL')
