# used Claude 4 Code to assist in this code and verified against docs and other examples from the web. No inappropriate data was shared in the process
from django.conf import settings
from django.views.generic import TemplateView
from django.shortcuts import redirect
from datetime import datetime
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from collections import defaultdict
from django.db.models import Q

from django.test import RequestFactory
from rest_framework.request import Request as DRFRequest

# integration_badges views
from integration_badges.views import (
    Roadmap_Full_v1,
    Resource_Roadmap_Badges_Status_v1
)

# cider views
from cider.views import CiderACCESSActiveGroups_v2_List


@method_decorator(cache_page(60 * 5), name='get')
class GroupBadgeStatusView(TemplateView):
    """Group badge view"""
    template_name = 'integration_views/group_pivot.html'

    def call_integration_group_views(self, view_class, **kwargs):
        """importing view content from integration_badges"""
        factory = RequestFactory()
        django_request = factory.get('/', kwargs)

        drf_request = DRFRequest(django_request)
        drf_request.user = self.request.user

        view = view_class()
        view.request = drf_request
        view.format_kwarg = None
        view.kwargs = kwargs

        response = view.get(drf_request, **kwargs)

        if hasattr(response, 'data'):
            data = response.data
            if isinstance(data, dict):
                return data.get('results', data.get('active_groups', []))
            return data
        return []

    def fetch_api_data(self, endpoint, params=None):
        """Fetch data from internal DRF views"""
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
            print(f"Error fetching {endpoint}: {e}")
            return []

    def calculate_group_badge_counts(self, group_resources, resource_badges, all_required_badge_ids, roadmap_badges_by_roadmap, resource_to_roadmap):
        """Calculate badge counts for a group, respecting roadmap associations"""
        available = 0
        in_progress = 0
        not_planned = 0
        required_available = 0
        total_required = len(all_required_badge_ids) * len(group_resources) if all_required_badge_ids else 0

        completed_statuses = {'verified', 'available', 'approved', 'complete', 'completed'}
        in_progress_statuses = {'planned', 'failed', 'testing', 'tasks-completed', 'tasls-completed', 'in-progress'}
        explicit_not_planned_statuses = {'not planned', 'not-planned'}

        for resource_id in group_resources:
            resource_badge_data = resource_badges.get(resource_id, {})
            resource_badge_ids = set(resource_badge_data.keys())

            resource_roadmap_id = resource_to_roadmap.get(resource_id)

            if resource_roadmap_id and resource_roadmap_id in roadmap_badges_by_roadmap:
                relevant_badge_ids = roadmap_badges_by_roadmap[resource_roadmap_id]
            else:
                relevant_badge_ids = set()

            for badge_id, status in resource_badge_data.items():
                status_lower = status.lower().strip()

                if status_lower in completed_statuses:
                    available += 1
                    if badge_id in all_required_badge_ids:
                        required_available += 1
                elif status_lower in in_progress_statuses:
                    in_progress += 1
                elif status_lower in explicit_not_planned_statuses or status_lower == '':
                    not_planned += 1

            missing_badges = relevant_badge_ids - resource_badge_ids
            not_planned += len(missing_badges)

        required_percentage = round((required_available / total_required * 100), 1) if total_required > 0 else 0

        return {
            'available': available,
            'in_progress': in_progress,
            'not_planned': not_planned,
            'required_available': required_available,
            'total_required': total_required,
            'required_percentage': required_percentage
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        groups_data = self.fetch_api_data('groups')

        if isinstance(groups_data, dict):
            if 'active_groups' in groups_data:
                groups_data = groups_data['active_groups']
            else:
                print(f"ERROR: groups_data is dict but no 'active_groups' key. Keys: {groups_data.keys()}")
                groups_data = []

        resource_roadmap_badges_data = self.fetch_api_data('resource_roadmap_badges')

        # Build resource-to-roadmap mapping
        resource_to_roadmap = {}
        for badge_record in resource_roadmap_badges_data:
            resource_id = str(badge_record.get('info_resourceid'))
            roadmap_id = badge_record.get('roadmap_id')
            if resource_id and roadmap_id:
                resource_to_roadmap[resource_id] = roadmap_id

        # Fetch roadmap badges using internal API
        roadmap_badges_by_roadmap = defaultdict(set)
        all_required_badge_ids = set()

        try:
            roadmaps = self.fetch_api_data('roadmaps')

            for roadmap in roadmaps:
                roadmap_id = roadmap.get('roadmap_id') or roadmap.get('id')
                if 'badges' in roadmap:
                    for badge_record in roadmap['badges']:
                        badge_id = str(badge_record.get('badge_id'))

                        if badge_id:
                            roadmap_badges_by_roadmap[roadmap_id].add(badge_id)

                            if badge_record.get('required', False):
                                all_required_badge_ids.add(badge_id)
        except Exception as e:
            print(f"ERROR fetching roadmap badges: {e}")

        resource_badges = defaultdict(dict)
        for badge_record in resource_roadmap_badges_data:
            resource_id = badge_record.get('info_resourceid')
            badge_id = str(badge_record.get('badge_id'))
            status = badge_record.get('status', '')
            if resource_id and badge_id:
                resource_badges[str(resource_id)][badge_id] = status

        group_stats = []
        preproduction_keywords = ['coming soon', 'coming-soon', 'coming_soon','pre-production', 'preproduction']

        for group in groups_data:
            if not isinstance(group, dict):
                print(f"WARNING: Skipping non-dict group: {type(group)} = {group}")
                continue

            group_resources = group.get('rollup_info_resourceids', [])

            if not group_resources:
                continue

            counts = self.calculate_group_badge_counts(
                group_resources,
                resource_badges,
                all_required_badge_ids,
                roadmap_badges_by_roadmap, 
                resource_to_roadmap
            )

            group_name = group.get('group_descriptive_name', '').lower()
            has_preproduction = any(keyword in group_name for keyword in preproduction_keywords)

            group_stats.append({
                'group_id': group.get('group_id'),
                'info_groupid': group.get('info_groupid'),
                'name': group.get('group_descriptive_name', 'Unknown Group'),
                'resource_count': len(group_resources),
                'has_preproduction': has_preproduction,
                **counts
            })

        group_stats.sort(key=lambda x: x['name'])

        context['group_stats'] = group_stats

        return context
