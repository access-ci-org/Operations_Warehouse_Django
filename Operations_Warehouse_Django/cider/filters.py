from django.db.models import Q
from cider.models import *
from itertools import chain

###############################################################################
# Active CiDeR Resource Filtering Criteria
#
# Arguments:
#   affiliation: ACCESS federated by default
#   type: resource type
#   result: return RESOURCEID, otherwise model objects by default
#
# With the ACTIVE status set being:
#   friendly | coming soon | pre-production | production | post-production
##
# NOTES:
#   list() forces evaluation so that we avoid issues with a sub-query in a different schema
###############################################################################

active_statuses = ('friendly', 'coming soon', 'pre-production', 'production', 'post-production')
allocated_types = ('Compute', 'Storage')

def CiderInfrastructure_ActiveAllocated_Filter(affiliation='ACCESS', result='OBJECTS'):
    resources = CiderInfrastructure.objects.filter(
            Q(cider_type__in=allocated_types) &
            Q(latest_status__in=active_statuses) &
            Q(project_affiliation__icontains=affiliation) )
    if result.upper() == 'RESOURCEID':
        return(list(resources.values_list('info_resourceid', flat=True)))
    else: # Model objects
        return(resources)

def CiderInfrastructure_Active_Filter(affiliation='ACCESS', result='OBJECTS', type='none', search=None):
    resources = CiderInfrastructure.objects.filter(
            Q(cider_type=type) &
            Q(latest_status__in=active_statuses) &
            Q(project_affiliation__icontains=affiliation) )
    if search:
        if type=='Science Gateway':
            resources = resources.filter(
                Q(info_resourceid__icontains=search) |
                Q(resource_descriptive_name__icontains=search) |
                Q(resource_description__icontains=search) |
                Q(other_attributes__short_name__icontains=search) |
                Q(other_attributes__long_description__icontains=search) )
        else:
            resources = resources.filter(
                Q(info_resourceid__icontains=search) |
                Q(resource_descriptive_name__icontains=search) |
                Q(resource_description__icontains=search) )
    if result.upper() == 'RESOURCEID':
        return(list(resources.values_list('info_resourceid', flat=True)))
    else: # Model objects
        return(resources)
