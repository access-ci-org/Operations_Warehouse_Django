# used Claude 4 Code to assist in this code and verified against docs and other examples from the web. No inappropriate data was shared in the process

from django.http import JsonResponse
from django.conf import settings
from django.views.generic import TemplateView
from django.shortcuts import redirect
from datetime import datetime
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from collections import defaultdict
from django.db.models import Q

# API View imports
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer

# Serializers
from drf_spectacular.utils import extend_schema, OpenApiParameter
from ..serializers import GroupPivotResponseSerializer

# integration_badges views
from integration_badges.views import (
    Roadmap_Full_v1,
    Resource_Roadmap_Badges_Status_v1
)

# cider views
from cider.views import CiderACCESSActiveGroups_v2_List

# cider models
from cider.models import CiderInfrastructure
from django.apps import apps

# logging for debugging
import logging
logger = logging.getLogger(__name__)

@method_decorator(cache_page(60 * 5), name='get')
class GroupBadgeStatusView(TemplateView):
    """Group badge view"""
    template_name = 'integration_views/group_pivot.html'

    def call_integration_group_views(self, view_class, **kwargs):
        """ """
        request = self.request
        if kwargs:
            from django.http import QueryDict
            query_dict = QueryDict('', mutable=True)
            query_dict.update(kwargs)
            request.GET = query_dict

        view = view_class.as_view()
        response = view(request, **kwargs)

        if hasattr(response, 'data'):
            data = response.data
            if isinstance(data, dict):
                return data.get('results', data.get('active_groups', []))
            return data
        return []

    def fetch_api_data(self, endpoint, params=None):
        """ """
        endpoint_mapping = {
            'groups': CiderACCESSActiveGroups_v2_List,
            'resource_roadmap_badges': Resource_Roadmap_Badges_Status_v1,
            'roadmaps': Roadmap_Full_v1,
        }

        view_class = endpoint_mapping.get(endpoint)
        if not view_class:
            return []

        try:
            data = self.call_integration_group_views(view_class, **(params or {}))

            # Handle groups endpoint special case
            if endpoint == 'groups' and isinstance(data, dict) and 'active_groups' in data:
                return data['active_groups']

            return data
        except Exception as e:
            logger.error(f"Error fetching {endpoint}: {e}")
            return []

    def calculate_group_badge_counts(self, group_resources, resource_badges, all_required_badge_ids, roadmap_badges_by_roadmap, resource_to_roadmap, resource_status_lookup, resource_type_lookup):
        """Calculate badge counts for a group, treating non-verified required badges as in-progress"""
        # DEBUG
        # print(f"DEBUG: calculate_group_badge_counts called with {len(group_resources)} resources: {group_resources}")

        available = 0
        in_progress = 0
        not_planned = 0
        verified_required = 0
        in_progress_required = 0

        completed_statuses = {'verified', 'available', 'approved', 'complete', 'completed'}
        in_progress_statuses = {'planned', 'failed', 'testing', 'tasks-completed', 'tasls-completed', 'in-progress'}
        explicit_not_planned_statuses = {'not planned', 'not-planned'}
        preproduction_statuses = {'pre-production', 'pre_production', 'coming soon', 'coming_soon'}

        # Default roadmap mapping by type
        type_to_roadmap = {
            'compute': 67,
            'storage': 68,
            'cloud': 34,
            'data': 68  # Adjust as needed
        }

        for resource_id in group_resources:
            resource_status = resource_status_lookup.get(str(resource_id), '').lower().strip()
            is_preproduction = resource_status in preproduction_statuses or any(keyword in resource_status for keyword in preproduction_statuses)

            resource_badge_data = resource_badges.get(str(resource_id), {})
            resource_roadmap_id = resource_to_roadmap.get(str(resource_id))

            # If no roadmap mapping, infer from cider_type
            if not resource_roadmap_id:
                resource_type = resource_type_lookup.get(str(resource_id), '').lower()
                resource_roadmap_id = type_to_roadmap.get(resource_type)
                # DEBUG
                # if resource_roadmap_id:
                    # print(f"Inferred roadmap {resource_roadmap_id} for {resource_id} (type={resource_type})")

            if resource_roadmap_id and resource_roadmap_id in roadmap_badges_by_roadmap:
                resource_required_badge_ids = roadmap_badges_by_roadmap[resource_roadmap_id]
            else:
                resource_required_badge_ids = set()

            # Track which required badges we've seen
            seen_required_badges = set()

            # Process existing badge records
            for badge_id, status in resource_badge_data.items():
                status_lower = status.lower().strip()

                # For NON-preproduction: count all badges by status
                if not is_preproduction:
                    if status_lower in completed_statuses:
                        available += 1
                    elif status_lower in in_progress_statuses:
                        in_progress += 1
                    elif status_lower in explicit_not_planned_statuses or status_lower == '':
                        not_planned += 1

                # For ALL resources: handle required badges
                if badge_id in resource_required_badge_ids:
                    seen_required_badges.add(badge_id)

                    if status_lower in completed_statuses:
                        verified_required += 1
                        # DEBUG
                        # if is_preproduction:
                        #     print(f"  Required badge {badge_id}: VERIFIED")
                    else:
                        in_progress_required += 1
                        # DEBUG
                        # if is_preproduction:
                        #     print(f"  Required badge {badge_id}: IN-PROGRESS (status={status})")

            # Count missing required badges as in-progress
            missing_required = resource_required_badge_ids - seen_required_badges
            if missing_required:
                in_progress_required += len(missing_required)
                # DEBUG
                # if is_preproduction:
                #     print(f"  Missing {len(missing_required)} required badges, counted as in-progress")

        # Total calculations
        in_progress += in_progress_required
        total_required = verified_required + in_progress_required
        required_percentage = round((verified_required / total_required * 100), 1) if total_required > 0 else 0

        return {
            'available': available, 
            'in_progress': in_progress, 
            'not_planned': not_planned,
            'verified_required': verified_required, 
            'in_progress_required': in_progress_required,
            'total_required': total_required,        
            'required_percentage': required_percentage,
        }



    def get_context_data(self, **kwargs):
        # DEBUG
        # print("DEBUG: get_context_data called")
        context = super().get_context_data(**kwargs)

        groups_data = self.fetch_api_data('groups')
        # DEBUG
        # print(f"DEBUG: Fetched {len(groups_data) if isinstance(groups_data, list) else 'non-list'} groups")

        if isinstance(groups_data, dict):
            if 'active_groups' in groups_data:
                groups_data = groups_data['active_groups']
            else:
                logger.error(f"groups_data is dict but no 'active_groups' key. Keys: {groups_data.keys()}")
                groups_data = []

        resource_roadmap_badges_data = self.fetch_api_data('resource_roadmap_badges')
        # DEBUG
        # print(f"DEBUG: Fetched {len(resource_roadmap_badges_data)} badge records")

        # Build resource-to-roadmap mapping
        resource_to_roadmap = {}
        for badge_record in resource_roadmap_badges_data:
            resource_id = badge_record.get('info_resourceid')
            roadmap_id = badge_record.get('roadmap_id')
            if resource_id is not None and roadmap_id is not None:
                resource_to_roadmap[str(resource_id)] = roadmap_id

        preproduction_statuses = ['pre-production', 'pre_production', 'coming soon', 'coming_soon']

        all_resources = CiderInfrastructure.objects.filter(
            Q(project_affiliation__icontains='ACCESS')
        ).values('info_resourceid', 'latest_status', 'cider_type')

        # DEBUG
        # print(f"DEBUG: Fetched {len(list(all_resources))} CiderInfrastructure records")

        resource_status_lookup = {}
        resource_type_lookup = {}

        for res in all_resources:
            resource_id = res.get('info_resourceid')
            if resource_id is not None:
                resource_status_lookup[str(resource_id)] = res.get('latest_status', '').lower().strip()
                resource_type_lookup[str(resource_id)] = res.get('cider_type', '').lower().strip()


        # Fetch roadmap badges
        roadmap_badges_by_roadmap = defaultdict(set)
        all_required_badge_ids = set()

        try:
            roadmaps = self.fetch_api_data('roadmaps')
            # DEBUG
            # print(f"DEBUG: Fetched {len(roadmaps)} roadmaps")

            draft_roadmap_ids = set()
            for roadmap in roadmaps:
                roadmap_id = roadmap.get('roadmap_id') or roadmap.get('id')
                if roadmap.get('status', '').lower() == 'draft':
                    draft_roadmap_ids.add(roadmap_id)

            for roadmap in roadmaps:
                roadmap_id = roadmap.get('roadmap_id') or roadmap.get('id')
                if 'badges' in roadmap:
                    for badge_record in roadmap['badges']:
                        badge_id = badge_record.get('badge_id')
                        if badge_id is not None:
                            badge_id_str = str(badge_id)
                            if badge_record.get('required', False):
                                roadmap_badges_by_roadmap[roadmap_id].add(badge_id_str)
                                all_required_badge_ids.add(badge_id_str)
        except Exception as e:
            logger.error(f"Error fetching roadmaps: {e}")
            roadmap_badges_by_roadmap = defaultdict(set)
            all_required_badge_ids = set()

        # DEBUG
        # print(f"DEBUG: Processed roadmaps, found {len(roadmap_badges_by_roadmap)} roadmap badge sets")

        resource_badges = defaultdict(dict)
        for badge_record in resource_roadmap_badges_data:
            resource_id = badge_record.get('info_resourceid')
            badge_id = badge_record.get('badge_id')
            status = badge_record.get('status', '')
            if resource_id is not None and badge_id is not None:
                resource_badges[str(resource_id)][str(badge_id)] = status

        group_stats = []
        # DEBUG
        # print(f"DEBUG: About to loop through {len(groups_data)} groups")

        for group in groups_data:
            if not isinstance(group, dict):
                logger.warning(f"Skipping non-dict group: {type(group)} = {group}")
                continue

            group_resources = group.get('rollup_info_resourceids', [])
            if not group_resources:
                # DEBUG
                # print(f"DEBUG: Skipping group with no resources")
                continue

            # Build group_roadmap_ids with inference
            group_roadmap_ids = set()
            type_to_roadmap = {
                'compute': 67,
                'storage': 68,
                'cloud': 34,
                'data': 68
            }

            for res_id in group_resources:
                # Try explicit mapping first
                roadmap_id = resource_to_roadmap.get(str(res_id))
                if roadmap_id:
                    group_roadmap_ids.add(roadmap_id)
                else:
                    # Try inference from cider_type
                    cider_type = resource_type_lookup.get(str(res_id), '').lower().strip()
                    inferred_roadmap = type_to_roadmap.get(cider_type)
                    if inferred_roadmap:
                        group_roadmap_ids.add(inferred_roadmap)
            # DEBUG
            # print(f"DEBUG: Group '{group.get('group_descriptive_name')}' roadmap_ids: {group_roadmap_ids}, draft_ids: {draft_roadmap_ids}")

            if group_roadmap_ids:
                if group_roadmap_ids.issubset(draft_roadmap_ids):
                    continue
            else:
                continue

            counts = self.calculate_group_badge_counts(
                group_resources,
                resource_badges,
                all_required_badge_ids,
                roadmap_badges_by_roadmap, 
                resource_to_roadmap,
                resource_status_lookup,
                resource_type_lookup
            )

            has_preproduction = False
            group_statuses = set()
            status_counts = defaultdict(int)

            for resource_id in group_resources:
                status = resource_status_lookup.get(str(resource_id), 'unknown')
                group_statuses.add(status)
                status_counts[status] += 1

                if (status in preproduction_statuses or
                    any(keyword in status for keyword in preproduction_statuses)):
                    has_preproduction = True

            if len(group_statuses) == 1:
                group_status = list(group_statuses)[0]
                has_mixed_status = False
            else:
                group_status = 'mixed'
                has_mixed_status = True

            group_stats.append({
                'group_id': group.get('group_id'),
                'info_groupid': group.get('info_groupid'),
                'name': group.get('group_descriptive_name', 'Unknown Group'),
                'resource_count': len(group_resources),
                'has_preproduction': has_preproduction,
                'group_status': group_status,
                'has_mixed_status': has_mixed_status,
                'status_breakdown': dict(status_counts),
                **counts
            })

        group_stats.sort(key=lambda x: x['name'])
        context['group_stats'] = group_stats

        return context

class GroupBadgeStatusAPI(GenericAPIView):
    """JSON API endpoint for group badge status"""
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]
    serializer_class = GroupPivotResponseSerializer

    @extend_schema(
        operation_id='group_pivot_json',
        description='Get group badge status data',
        responses={200: GroupPivotResponseSerializer}
    )
    def get(self, request):
        view = GroupBadgeStatusView()
        view.request = request._request
        view.kwargs = {}

        context = view.get_context_data()
        group_stats = context.get('group_stats', [])

        return Response({
            'groups': group_stats,
            'selected_group': None,
            'pivot_data': {},
            'badges_list': [],
            'completed_badges': sum(g.get('verified_required', 0) for g in group_stats),
            'in_progress_badges': sum(g.get('in_progress_required', 0) for g in group_stats),
        })
