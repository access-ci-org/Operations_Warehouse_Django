from django.db.models import Q
from cider.models import *
from itertools import chain

###############################################################################
# Active CiDeR Resource Filtering Criteria
#
# Arguments:
#   affiliation: ACCESS federated, otherwise ALL
#   type: SUB=sub-resources only, otherwise ALL (parent and sub)
#   result: return RESOURCEID, otherwise model objects by default
#
# With the ACTIVE status set being:
#   friendly | coming soon | pre-production | production | post-production
#
# An Active BASE RESOURCE is
#      cider_type='resource'
#  and xsede_services_only is False (True means this isn't a user facing service)
#  and provider_level in ['XSEDE Level 1', 'XSEDE Level 2']
#  and current_statuses in ACTIVE status set
#
# An Active SUB-RESOURCE of the above BASE RESOURCES is ONE of:
#      cider_type='compute'
#   and current_statuses in ACTIVE status set
#   and other_attributes.is_visualization is True
# OR
#      cider_type='compute'
#   and current_statuses in ACTIVE status set
#   and other_attributes.allocations_info.allocable_type = 'ComputeResource'
# OR
#      cider_type='storage'
#   and current_statuses in ACTIVE status set
#
# NOTES:
#   list() forces evaluation so that we avoid issues with a sub-query in a different schema
###############################################################################

active_statuses = ('friendly', 'coming soon', 'pre-production', 'production', 'post-production')
allocated_types = ('Compute', 'Storage')

def CiderInfrastructure_AllocatedResources(affiliation='ACCESS', result='OBJECTS'):
    resources = CiderInfrastructure.objects.filter(
        Q(cider_type__in=allocated_types) &
        Q(latest_status__in=active_statuses) &
        Q(project_affiliation__icontains=affiliation)
    )
    if result.upper() == 'RESOURCEID':
        return(list(resources.values_list('info_resourceid', flat=True)))
    else: # Model objects
        return(resources)
            
# Introduced 2022-04-30 by JP for ACCESS
def CiderInfrastructure_ActiveOnlineServices(affiliation='ACCESS', result='OBJECTS'):
    # Active sub-resources of the desired type
    resources = CiderInfrastructure.objects.filter(
            Q(cider_type='Online Service') &
            Q(latest_status__in=active_statuses) &
            Q(project_affiliation__icontains=affiliation)
        )
    if result.upper() == 'RESOURCEID':
        return(list(resources.values_list('info_resourceid', flat=True)))
    else: # Model objects
        return(resources)
