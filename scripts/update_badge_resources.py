#!/usr/bin/env python3
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Operations_Warehouse_Django.settings")
django.setup()

from django.db.models import Q

from cider.models import *
from integration_badges.models import *

import pdb
pdb.set_trace()

badging_types = ('Compute', 'Storage')
resources = CiderInfrastructure.objects.filter(
    Q(cider_type__in=badging_types) & Q(project_affiliation__icontains='ACCESS') )

cider_infoid_map = { i.cider_resource_id: i.info_resourceid for i in resources }
cider_type_map = { i.cider_resource_id: i.cider_type for i in resources }

for item in Integration_Resource_Roadmap.objects.all():
    try:
        id = item.resource_id.cider_resource_id
        item.info_resourceid = cider_infoid_map[id]
        if cider_type_map[id] == 'Storage':
            item.roadmap_id_id = 68
        elif item.info_resourceid.startswith('jetstream2'):
            item.roadmap_id_id = 34
        item.save()
    except Exception as e:
        print(f'{type(e).__name__} saving Integration_Resource_Roadmap resource_id={id}')

for item in Integration_Resource_Badge.objects.all():
    try:
        id = item.resource_id.cider_resource_id
        item.info_resourceid = cider_infoid_map[id]
        if cider_type_map[id] == 'Storage':
            item.roadmap_id_id = 68
        elif item.info_resourceid.startswith('jetstream2'):
            item.roadmap_id_id = 34
        item.save()
    except Exception as e:
        print(f'{type(e).__name__} saving Integration_Resource_Badge resource_id={id}')

for item in Integration_Badge_Workflow.objects.all():
    try:
        id = item.resource_id.cider_resource_id
        item.info_resourceid = cider_infoid_map[id]
        if cider_type_map[id] == 'Storage':
            item.roadmap_id_id = 68
        elif item.info_resourceid.startswith('jetstream2'):
            item.roadmap_id_id = 34
        item.save()
    except Exception as e:
        print(f'{type(e).__name__} saving Integration_Badge_Workflow resource_id={id}')

for item in Integration_Badge_Task_Workflow.objects.all():
    try:
        id = item.resource_id.cider_resource_id
        item.info_resourceid = cider_infoid_map[id]
        if cider_type_map[id] == 'Storage':
            item.roadmap_id_id = 68
        elif item.info_resourceid.startswith('jetstream2'):
            item.roadmap_id_id = 34
        item.save()
    except Exception as e:
        print(f'{type(e).__name__} saving Integration_Badge_Task_Workflow resource_id={id}')

