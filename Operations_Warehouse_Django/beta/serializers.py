from datetime import datetime
from django.urls import reverse
from django.utils.encoding import uri_to_iri
from cider.models import *
from glue2.models import ComputingManager, ExecutionEnvironment
from rest_framework import serializers

class SGCI_Resource_100_Serializer(serializers.ModelSerializer):
    REMOVABLE_FIELDS = ['computeResources', 'storageResources', 'resourceOutages']
    schemaVersion = serializers.SerializerMethodField()
    host = serializers.CharField(source='info_resourceid')
    name = serializers.CharField(source='resource_descriptive_name')
    description = serializers.CharField(source='resource_description')
    computeResources = serializers.SerializerMethodField()
    storageResources = serializers.SerializerMethodField()
    resourceStatus = serializers.SerializerMethodField()
    resourceOutages = serializers.SerializerMethodField()
    class Meta:
        model = CiderInfrastructure
        fields = ('schemaVersion', 'host', 'name', 'description', 'computeResources', 'storageResources', 'resourceStatus', 'resourceOutages')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        for field in self.REMOVABLE_FIELDS:
            try:
                if rep[field] is None:
                    rep.pop(field)
            except KeyError:
                pass
        return rep
        
    def get_schemaVersion(self, CiderResource):
        return('1.0.0')

    def get_computeResources(self, CiderResource):
        if CiderResource.cider_type != 'compute':
            return(None)

        connections = []
        # Legacy XSEDE_Information_Warehouse/django_xsede_warehouse/warehouse_views code removed

        batchSystem = {}
        cm = ComputingManager.objects.filter(ResourceID=CiderResource.info_resourceid)
        if cm and cm[0].Name:
            batchSystem['jobManager'] = cm[0].Name
        else:
            batchSystem['jobManager'] = CiderResource.other_attributes.get('batch_system', 'N/A')

        evs = ExecutionEnvironment.objects.filter(ResourceID=CiderResource.info_resourceid)
        partitions = []
        for ev in evs:
            totalNodes = ev.EntityJSON.get('TotalInstances')
            if not totalNodes:
                extension = ev.EntityJSON.get('Extension')
                if extension and extension.get('Nodes'):
                    totalNodes = len(extension.get('Nodes'))
            cpuCount = ev.EntityJSON.get('LogicalCPUs')
            par = {'name': ev.Name,
                    'nodeHardware': {
                        'cpuType': ev.EntityJSON.get('Platform', 'n/a'),
                        'memorySize': ev.EntityJSON.get('MainMemorySize', 'n/a') }
                }
            if totalNodes:
                par['totalNodes'] = totalNodes
            if cpuCount:
                par['nodeHardware']['cpuCount'] = cpuCount
            partitions.append(par)
        if partitions:
            batchSystem['partitions'] = partitions

        batch = {'schedulerType': 'BATCH'}
        if connections:
            batch['connections'] = connections
        if batchSystem:
            batch['batchSystem'] = batchSystem

        fork = {'schedulerType': 'FORK',
                'forkSystem': {'systemType': 'LINUX'}
            }
        if connections:
            fork['connections'] = connections

        result = [batch, fork]
        return(result)

    def get_storageResources(self, CiderResource):
        if CiderResource.cider_type != 'storage':
            return(None)

        connections = []
        # Legacy XSEDE_Information_Warehouse/django_xsede_warehouse/warehouse_views code emoved

        storage = {'storageType': 'POSIX'}
        if connections:
            storage['connections'] = connections

        result = [storage]
        return(result)

    def get_resourceStatus(self, CiderResource):
        status = {'status': CiderResource.latest_status.capitalize()}
        if CiderResource.latest_status_begin:
            status['starts'] = '{:%Y-%m-%d}'.format(CiderResource.latest_status_begin)
        if CiderResource.latest_status_end:
            status['ends'] = '{:%Y-%m-%d}'.format(CiderResource.latest_status_end)
        return(status)

    def get_resourceOutages(self, CiderResource):
        now = timezone.now()
        outages = []
        # current and future outages all end in the future
        # Legacy XSEDE_Information_Warehouse/django_xsede_warehouse/warehouse_views code to populate removed
        if outages:
            return(outages)
        else:
            return(None)
