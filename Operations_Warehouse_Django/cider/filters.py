from django.db.models import Q
from cider.models import *
from itertools import chain

###############################################################################
# Active CiDeR Resource Filtering Criteria
#
# Arguments:
#   affiliation: XSEDE federated, otherwise ALL
#   allocated: True=allocated Level 1 and 2, otherwise ALL
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
# 2017-10-17 JP Add "Q(other_attributes__is_allocated=True)" to filter out Beacon compute and similar
###############################################################################

# Not Active_Sub or Active_All

def CiderInfrastructure_Active(affiliation='ACCESS', allocated=True, type='SUB', result='OBJECTS'):
    # Active base resources
    #  Q(cider_type='resource') & # removed 10-25-2022 by JP
    if allocated:
        parent_resources = CiderInfrastructure.objects.filter(
                                                Q(cider_type='resource') &
                                                Q(project_affiliation__icontains=affiliation) &
                                                Q(other_attributes__xsede_services_only=False) &
                                                (Q(provider_level='XSEDE Level 1') |
                                                 Q(provider_level='XSEDE Level 2')) &
                                                ~Q(info_resourceid='stand-alone.tg.teragrid.org') &
                                                ~Q(info_resourceid='futuregrid0.futuregrid.xsede.org') &
                                                ~Q(info_resourceid='Abe-QB-Grid.teragrid.org') &
                                                (Q(current_statuses__icontains='friendly') |
                                                 Q(current_statuses__icontains='coming soon') |
                                                 Q(current_statuses__icontains='pre-production') |
                                                 Q(current_statuses__istartswith='production') |
                                                 Q(current_statuses__icontains=',production') |
                                                 Q(current_statuses__icontains='post-production'))
                                                    )
    else:
        parent_resources = CiderInfrastructure.objects.filter(
                                                Q(cider_type='resource') &
                                                Q(project_affiliation__icontains=affiliation) &
                                                Q(other_attributes__xsede_services_only=False) &
                                                ~Q(info_resourceid='stand-alone.tg.teragrid.org') &
                                                ~Q(info_resourceid='futuregrid0.futuregrid.xsede.org') &
                                                ~Q(info_resourceid='Abe-QB-Grid.teragrid.org') &
                                                (Q(current_statuses__icontains='friendly') |
                                                 Q(current_statuses__icontains='coming soon') |
                                                 Q(current_statuses__icontains='pre-production') |
                                                 Q(current_statuses__istartswith='production') |
                                                 Q(current_statuses__icontains=',production') |
                                                 Q(current_statuses__icontains='post-production'))
                                                    )
    parent_ids = parent_resources.values_list('cider_resource_id', flat=True)
    # Active sub-resources of active parent resources
    if allocated:
        child_resource = CiderInfrastructure.objects.filter(
                                                Q(parent_resource__in=parent_ids) &
                                                Q(other_attributes__is_allocated=True) &
                                                (Q(current_statuses__icontains='friendly') |
                                                 Q(current_statuses__icontains='coming soon') |
                                                 Q(current_statuses__icontains='pre-production') |
                                                 Q(current_statuses__istartswith='production') |
                                                 Q(current_statuses__icontains=',production') |
                                                 Q(current_statuses__icontains='post-production')) &
                                                ((Q(cider_type='compute') & Q(other_attributes__is_visualization=True)) |
                                                 (Q(cider_type='compute') & Q(other_attributes__allocations_info__allocable_type='ComputeResource')) |
                                                 (Q(cider_type='storage'))
                                                )
                                                   )
    else:
        child_resource = CiderInfrastructure.objects.filter(
                                                Q(parent_resource__in=parent_ids) &
                                                (Q(current_statuses__icontains='friendly') |
                                                 Q(current_statuses__icontains='coming soon') |
                                                 Q(current_statuses__icontains='pre-production') |
                                                 Q(current_statuses__istartswith='production') |
                                                 Q(current_statuses__icontains=',production') |
                                                 Q(current_statuses__icontains='post-production')) &
                                                (Q(cider_type='compute') | Q(cider_type='storage'))
                                                   )
    if result.upper() == 'RESOURCEID':
        if type.upper() == 'SUB':
            return(list(child_resource.values_list('info_resourceid', flat=True)))
        elif type.upper() == 'BASE':
            return(list(parent_resources.values_list('info_resourceid', flat=True)))
        else:
            return(list(chain(parent_resources.values_list('info_resourceid', flat=True), \
                              child_resource.values_list('info_resourceid', flat=True))))
    else: # Model objects
        if type.upper() == 'SUB':
            return(child_resource)
        elif type.upper() == 'BASE':
            return(parent_resources)
        else:
            return(parent_resources | child_resource)

# Introduced 2020-02-23 by JP in support of SGCI resource description view
# Looks at the latest_status instead of current_statuses which excludes dual decomissioned + other status (likely invalid)
# Doesn't filter by provider_level
# This should replace the above filter eventually
def CiderInfrastructure_Active_V2(affiliation='XSEDE', allocated=True, type='SUB', result='OBJECTS'):
    # Active base resources
    if allocated:
        parent_resources = CiderInfrastructure.objects.filter(
                                                Q(cider_type='resource') &
                                                Q(project_affiliation__icontains=affiliation) &
                                                Q(other_attributes__xsede_services_only=False) &
#                                                (Q(provider_level='XSEDE Level 1') |
#                                                 Q(provider_level='XSEDE Level 2')) &
                                                ~Q(info_resourceid='stand-alone.tg.teragrid.org') &
                                                ~Q(info_resourceid='futuregrid0.futuregrid.xsede.org') &
                                                ~Q(info_resourceid='Abe-QB-Grid.teragrid.org') &
                                                (Q(latest_status='friendly') |
                                                 Q(latest_status='coming soon') |
                                                 Q(latest_status='pre-production') |
                                                 Q(latest_status='production') |
                                                 Q(latest_status='post-production'))
                                                    )
    else:
        parent_resources = CiderInfrastructure.objects.filter(
                                                Q(cider_type='resource') &
                                                Q(project_affiliation__icontains=affiliation) &
                                                Q(other_attributes__xsede_services_only=False) &
                                                ~Q(info_resourceid='stand-alone.tg.teragrid.org') &
                                                ~Q(info_resourceid='futuregrid0.futuregrid.xsede.org') &
                                                ~Q(info_resourceid='Abe-QB-Grid.teragrid.org') &
                                                (Q(latest_status='friendly') |
                                                 Q(latest_status='coming soon') |
                                                 Q(latest_status='pre-production') |
                                                 Q(latest_status='production') |
                                                 Q(latest_status='post-production'))
                                                    )
    parent_ids = parent_resources.values_list('cider_resource_id', flat=True)
    # Active sub-resources of active parent resources
    if allocated:
        child_resource = CiderInfrastructure.objects.filter(
                                                Q(parent_resource__in=parent_ids) &
                                                Q(other_attributes__is_allocated=True) &
                                                (Q(latest_status='friendly') |
                                                 Q(latest_status='coming soon') |
                                                 Q(latest_status='pre-production') |
                                                 Q(latest_status='production') |
                                                 Q(latest_status='post-production')) &
                                                ((Q(cider_type='compute') & Q(other_attributes__is_visualization=True)) |
                                                 (Q(cider_type='compute') & Q(other_attributes__allocations_info__allocable_type='ComputeResource')) |
                                                 (Q(cider_type='storage'))
                                                )
                                                   )
    else:
        child_resource = CiderInfrastructure.objects.filter(
                                                Q(parent_resource__in=parent_ids) &
                                                (Q(latest_status='friendly') |
                                                 Q(latest_status='coming soon') |
                                                 Q(latest_status='pre-production') |
                                                 Q(latest_status='production') |
                                                 Q(latest_status='post-production')) &
                                                (Q(cider_type='compute') | Q(cider_type='storage'))
                                                   )
    if result.upper() == 'RESOURCEID':
        if type.upper() == 'SUB':
            return(list(child_resource.values_list('info_resourceid', flat=True)))
        else:
            return(list(chain(parent_resources.values_list('info_resourceid', flat=True), \
                              child_resource.values_list('info_resourceid', flat=True))))
    else: # Model objects
        if type.upper() == 'SUB':
            return(child_resource)
        else:
            return(parent_resources | child_resource)

