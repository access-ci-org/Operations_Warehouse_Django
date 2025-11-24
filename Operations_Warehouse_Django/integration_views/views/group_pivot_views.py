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
import sys

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

    def calculate_group_badge_counts(self, group_resources, resource_badges, 
                                    all_required_badge_ids, roadmap_badges_by_roadmap,
                                    resource_to_roadmap, resource_status_lookup, 
                                    resource_type_lookup):
        """Calculate badge counts for a resource group"""

        available_count = 0
        in_progress_count = 0
        required_verified = 0

        completed_statuses = {'verified'}
        excluded_statuses = {'not planned', 'not-planned', ''}

        # DEBUG
        print(f"\n=== GROUP BADGE COUNT DEBUG ===", file=sys.stderr)
        print(f"Processing {len(group_resources)} resources", file=sys.stderr)

        for resource_id in group_resources:
            badge_statuses = resource_badges.get(resource_id, {})
            roadmap_id = resource_to_roadmap.get(resource_id)
            required_badge_ids = roadmap_badges_by_roadmap.get(roadmap_id, set())

            # DEBUG
            # print(f"\n  Resource: {resource_id}", file=sys.stderr)
            # print(f"    Roadmap ID: {roadmap_id}", file=sys.stderr)
            # print(f"    Required badge IDs: {required_badge_ids}", file=sys.stderr)
            # print(f"    Badge statuses count: {len(badge_statuses)}", file=sys.stderr)

            # Get badge IDs this resource already has records for
            existing_badge_ids = set(badge_statuses.keys())
            print(f"    Existing badge IDs: {existing_badge_ids}", file=sys.stderr)


            # Get verified badge IDs for this resource
            verified_badge_ids = {
                badge_id for badge_id, status in badge_statuses.items()
                if status and status.lower().strip() in completed_statuses
            }
            print(f"    Verified badge IDs: {verified_badge_ids}", file=sys.stderr)

            # Process explicit badge records
            for badge_id, status in badge_statuses.items():
                status_lower = status.lower().strip() if status else ''
                is_required = str(badge_id) in required_badge_ids

                if status_lower in completed_statuses:
                    available_count += 1
                    if is_required:
                        required_verified += 1
                elif status_lower and status_lower not in excluded_statuses:
                    if not is_required:  # Only optional badges
                        in_progress_count += 1

            # implicit in-progress badges for missing required badges
            non_verified_required = required_badge_ids - {str(bid) for bid in verified_badge_ids}
            missing_required = non_verified_required - {str(bid) for bid in existing_badge_ids}

            in_progress_count += len(missing_required)

        # Calculate required_total
        required_total = 0
        for resource_id in group_resources:
            roadmap_id = resource_to_roadmap.get(resource_id)
            if roadmap_id:
                required_badge_ids = roadmap_badges_by_roadmap.get(roadmap_id, set())
                required_total += len(required_badge_ids)

        return available_count, in_progress_count, required_verified, required_total


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        groups_data = self.fetch_api_data('groups')

        if isinstance(groups_data, dict):
            if 'active_groups' in groups_data:
                groups_data = groups_data['active_groups']
            else:
                logger.error(f"groups_data is dict but no 'active_groups' key. Keys: {groups_data.keys()}")
                groups_data = []

        roadmaps_data = self.fetch_api_data('roadmaps')
        resource_roadmap_badges_data = self.fetch_api_data('resource_roadmap_badges')


        # Build resource_to_roadmap from explicit badge records
        resource_to_roadmap = {}
        for badge_record in resource_roadmap_badges_data:
            resource_id = badge_record.get('info_resourceid')
            roadmap_id = badge_record.get('roadmap_id')
            if resource_id and roadmap_id:
                resource_to_roadmap[str(resource_id)] = roadmap_id

        # Map roadmap names to IDs
        type_to_roadmap = {}
        for roadmap in roadmaps_data:
            roadmap_name = roadmap.get('name', '').lower()
            roadmap_id = roadmap.get('roadmap_id') or roadmap.get('id')

            if 'compute' in roadmap_name:
                type_to_roadmap['compute'] = roadmap_id
            elif 'storage' in roadmap_name:
                type_to_roadmap['storage'] = roadmap_id
            elif 'cloud' in roadmap_name:
                type_to_roadmap['cloud'] = roadmap_id

        # Get resource status and type from database
        all_resources = CiderInfrastructure.objects.filter(
            Q(project_affiliation__icontains='ACCESS')
        ).values('info_resourceid', 'latest_status', 'cider_type')

        resource_status_lookup = {}
        resource_type_lookup = {}

        for res in all_resources:
            resource_id = res.get('info_resourceid')
            if resource_id is not None:
                resource_status_lookup[str(resource_id)] = res.get('latest_status', '').lower().strip()
                resource_type_lookup[str(resource_id)] = res.get('cider_type', '').lower().strip()

        # Add cider_type-based mapping for resources without explicit roadmap assignment
        for resource_id, cider_type in resource_type_lookup.items():
            if resource_id not in resource_to_roadmap:
                if cider_type in type_to_roadmap:
                    resource_to_roadmap[resource_id] = type_to_roadmap[cider_type]

        preproduction_statuses = ['pre-production', 'pre_production', 'coming soon', 'coming_soon']


        all_resources = CiderInfrastructure.objects.filter(
            Q(project_affiliation__icontains='ACCESS')
        ).values('info_resourceid', 'latest_status', 'cider_type')

        resource_status_lookup = {}
        resource_type_lookup = {}

        for res in all_resources:
            resource_id = res.get('info_resourceid')
            if resource_id is not None:
                resource_status_lookup[str(resource_id)] = res.get('latest_status', '').lower().strip()
                resource_type_lookup[str(resource_id)] = res.get('cider_type', '').lower().strip()

        roadmap_badges_by_roadmap = defaultdict(set)
        all_required_badge_ids = set()

        try:
            roadmaps = self.fetch_api_data('roadmaps')

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

        resource_badges = defaultdict(dict)
        for badge_record in resource_roadmap_badges_data:
            resource_id = badge_record.get('info_resourceid')
            badge_id = badge_record.get('badge_id')
            status = badge_record.get('status', '')
            if resource_id is not None and badge_id is not None:
                resource_badges[str(resource_id)][str(badge_id)] = status

        group_stats = []

        for group in groups_data:
            if not isinstance(group, dict):
                logger.warning(f"Skipping non-dict group: {type(group)} = {group}")
                continue

            group_resources = group.get('rollup_info_resourceids', [])
            if not group_resources:
                continue

            group_roadmap_ids = set()
            type_to_roadmap = {
                'compute': 67,
                'storage': 68,
                'cloud': 34,
                'data': 68
            }

            for res_id in group_resources:
                roadmap_id = resource_to_roadmap.get(str(res_id))
                if roadmap_id:
                    group_roadmap_ids.add(roadmap_id)
                else:
                    cider_type = resource_type_lookup.get(str(res_id), '').lower().strip()
                    inferred_roadmap = type_to_roadmap.get(cider_type)
                    if inferred_roadmap:
                        group_roadmap_ids.add(inferred_roadmap)

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

            available_count, in_progress_count, required_verified, required_total = counts

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
                'available': available_count,
                'in_progress': in_progress_count,
                'verified_required': required_verified,
                'total_required': required_total,
                'required_percentage': round((required_verified / required_total * 100), 1) if required_total > 0 else 0
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
            'in_progress_badges': sum(g.get('in_progress', 0) for g in group_stats),
        })
