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

# serializers and API stuff
from drf_spectacular.utils import extend_schema, OpenApiParameter
from ..serializers import ResourcePivotResponseSerializer

# integration_badges views
from integration_badges.views import (
    Roadmap_Full_v1,
    Badge_Full_v1,
    Resource_Full_v1,
    Resource_Roadmap_Badges_Status_v1,
)

from cider.models import CiderInfrastructure
from cider.serializers import CiderInfrastructure_Summary_Serializer
from itertools import chain

# cider views import
from cider.views import (
    CiderACCESSActiveGroups_v2_List,
    CiderInfrastructure_v2_ACCESSAllList,
)

# logging DEBUG
import logging
logger = logging.getLogger(__name__)


@method_decorator(cache_page(60 * 5), name='get')
class RoadmapResourceBadgesView(TemplateView):
    """Resource badge status view"""
    template_name = 'integration_views/resource_pivot.html'
    DEFAULT_ROADMAP = 67


    def call_integration_badges_views(self, view_class, **kwargs):
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
                return data.get('results', [])
            return data
        return []


    def fetch_api_data(self, endpoint, params=None):
        """ """

        # Special handling for resources - get ALL types
        if endpoint == 'resources':
            return self.get_all_cider_resources()

        endpoint_mapping = {
            'roadmaps': Roadmap_Full_v1,
            'badges': Badge_Full_v1,
            'resource_roadmap_badges': Resource_Roadmap_Badges_Status_v1,
        }

        view_class = endpoint_mapping.get(endpoint)
        if not view_class:
            return []

        try:
            return self.call_integration_badges_views(view_class, **(params or {}))
        except Exception as e:
            print(f"Error fetching {endpoint}: {e}")
            return []


    def get_all_cider_resources(self):
        """Get ALL ACCESS resources from CiDeR, including pre-production, excluding decommissioned"""

        # Custom status list for this view - includes pre-production variations
        active_statuses_for_view = (
            'friendly',
            'coming soon',
            'coming_soon',
            'pre-production',
            'pre_production',
            'production',
            'post-production',
            'post_production'
        )

        resources = CiderInfrastructure.objects.filter(
            Q(project_affiliation__icontains='ACCESS')
        ).exclude(
            Q(latest_status__iexact='decommissioned') |
            Q(latest_status__iexact='retired')
        )

        serializer = CiderInfrastructure_Summary_Serializer(
            resources,
            context={'request': self.request},
            many=True
        )

        data = serializer.data

        # Filter serialized data by fixed_status (handles NULL latest_status cases)
        filtered_data = [
            r for r in data 
            if r.get('fixed_status', '').lower() in [s.lower() for s in active_statuses_for_view]
        ]

        # DEBUG
        # print(f"Resources: {len(filtered_data)} (excluded decommissioned)")

        return filtered_data


    def build_lookups(self, badges_data, resources_data):
        badge_lookup = {}
        for badge in badges_data:
            badge_id = badge.get('id') or badge.get('badge_id')
            # Validation
            if badge_id is not None:
                badge_lookup[str(badge_id)] = badge.get('name', 'Unknown Badge')

        resource_lookup = {}
        for res in resources_data:
            resource_id = res.get('info_resourceid') or res.get('resource_id')
            # Validation
            if resource_id is not None:
                resource_lookup[str(resource_id)] = res

        return badge_lookup, resource_lookup


    def process_roadmap_data(self, selected_roadmap, resource_roadmap_badges_data, badge_lookup, resource_lookup, resources_data, preproduction_by_roadmap):
        """Process and pivot data for the selected roadmap"""
        try:
            selected_roadmap_int = int(selected_roadmap)
        except (ValueError, TypeError):
            return {}, {}

        preproduction_resource_ids = set()
        if selected_roadmap_int in preproduction_by_roadmap:
            preproduction_resource_ids = {
                str(res['resource_info'].get('info_resourceid') or res['resource_info'].get('resource_id'))
                for res in preproduction_by_roadmap[selected_roadmap_int]
            }

        roadmap_badges = [item for item in resource_roadmap_badges_data 
                        if item.get('roadmap_id') == selected_roadmap_int]

        resource_ids_with_badges = {
            str(item.get('info_resourceid')) 
            for item in roadmap_badges 
            if item.get('info_resourceid') is not None
}

        all_resource_ids = resource_ids_with_badges | preproduction_resource_ids

        valid_resource_ids = {resource_id for resource_id in all_resource_ids 
                            if resource_id in resource_lookup}

        pivot_data = {}
        for resource_id in valid_resource_ids:
            resource_info = resource_lookup[resource_id]

            resource_badges = [item for item in roadmap_badges 
                            if str(item.get('info_resourceid')) == resource_id]

            badge_statuses = {}
            for rb in resource_badges:
                badge_id = rb.get('badge_id')
                # Validation fire
                if badge_id is not None:
                    badge_statuses[str(badge_id)] = rb.get('status')


            latest_status_begin_str = resource_info.get('latest_status_begin')
            latest_status_begin_date = None

            if latest_status_begin_str:
                try:
                    latest_status_begin_date = datetime.strptime(latest_status_begin_str, '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    latest_status_begin_date = None

            pivot_data[resource_id] = {
                'resource_info': resource_info,
                'badge_statuses': badge_statuses,
                'fixed_status': resource_info.get('fixed_status'),
                'latest_status_begin': latest_status_begin_date,
                'is_preproduction': resource_id in preproduction_resource_ids
            }

        pivot_data = dict(sorted(pivot_data.items(), 
                            key=lambda x: x[1]['resource_info'].get('resource_descriptive_name', '').lower()))

        all_valid_resource_ids = {str(res.get('info_resourceid') or res.get('resource_id'))
                                for res in resources_data 
                                if res.get('info_resourceid') or res.get('resource_id')}

        resources_without_badges = [
            resource_lookup[resource_id]
            for resource_id in sorted(all_valid_resource_ids - valid_resource_ids)
            if resource_id in resource_lookup
        ]

        return pivot_data, resources_without_badges


    def get_preproduction_resources(self, resources_data, resource_roadmap_badges_data, roadmaps_data):
        """Get all pre-production resources grouped by roadmap"""
        # Update status list to match actual values
        preproduction_statuses = ['pre-production', 'pre_production', 'coming soon', 'coming_soon']

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
            elif 'data' in roadmap_name:
                type_to_roadmap['data'] = roadmap_id

        resource_to_roadmap = {}
        for badge_record in resource_roadmap_badges_data:
            # Get values 
            resource_id = badge_record.get('info_resourceid')
            roadmap_id = badge_record.get('roadmap_id')
            # Validation
            if resource_id is not None and roadmap_id is not None:
                resource_to_roadmap[str(resource_id)] = roadmap_id

        preproduction_by_roadmap = {}

        for res in resources_data:
            resource_id = str(res.get('info_resourceid') or res.get('resource_id'))
            fixed_status = res.get('fixed_status', '').lower().strip()
            latest_status = res.get('latest_status', '').lower().strip()

            # Check both with spaces and underscores
            if (fixed_status in preproduction_statuses or 
                latest_status in preproduction_statuses or
                'pre-production' in fixed_status or
                'pre_production' in fixed_status or
                'coming soon' in fixed_status or
                'coming_soon' in fixed_status or
                'pre-production' in latest_status or
                'pre_production' in latest_status or
                'coming soon' in latest_status or
                'coming_soon' in latest_status):

                roadmap_id = resource_to_roadmap.get(resource_id)

                if not roadmap_id:
                    cider_type = res.get('cider_type', '').lower()
                    roadmap_id = type_to_roadmap.get(cider_type)

                if roadmap_id:
                    latest_status_begin_str = res.get('latest_status_begin')
                    latest_status_begin_date = None

                    if latest_status_begin_str:
                        try:
                            latest_status_begin_date = datetime.strptime(latest_status_begin_str, '%Y-%m-%d').date()
                        except (ValueError, TypeError):
                            latest_status_begin_date = None

                    resource_data = {
                        'resource_info': res,
                        'fixed_status': res.get('fixed_status'),
                        'latest_status_begin': latest_status_begin_date
                    }

                    if roadmap_id not in preproduction_by_roadmap:
                        preproduction_by_roadmap[roadmap_id] = []
                    preproduction_by_roadmap[roadmap_id].append(resource_data)

        for roadmap_id in preproduction_by_roadmap:
            preproduction_by_roadmap[roadmap_id] = sorted(
                preproduction_by_roadmap[roadmap_id],
                key=lambda x: (x['fixed_status'], x['resource_info'].get('resource_descriptive_name', ''))
            )

        return preproduction_by_roadmap


    def fetch_roadmap_badges_data(self, selected_roadmap):
        """Fetch roadmap-specific badge data with required field"""
        try:
            selected_roadmap_int = int(selected_roadmap)

            roadmaps_list = self.fetch_api_data('roadmaps')
            for roadmap in roadmaps_list:
                if roadmap.get('roadmap_id') == selected_roadmap_int:
                    if 'badges' in roadmap:
                        return roadmap.get('badges', [])
                    break

            return []
        except (ValueError, TypeError):
            return []


    def calculate_badge_status_counts(self, selected_roadmap, resource_roadmap_badges_data, roadmap_badges_data, pivot_data):
        """Count completed and in-progress badges for all resources, including pre-production missing badges"""
        try:
            selected_roadmap_int = int(selected_roadmap)
        except (ValueError, TypeError):
            return 0, 0

        completed_count = 0
        in_progress_count = 0

        completed_statuses = {'verified', 'tasks-completed', 'complete', 'completed'}
        excluded_statuses = {'not planned', 'not-planned', ''}

        # Get required badge IDs for this roadmap
        required_badge_ids = {
            str(badge.get('badge_id')) 
            for badge in roadmap_badges_data 
            if badge.get('required', False) and badge.get('badge_id') is not None
        }

        # Count badges from explicit records
        for badge_record in resource_roadmap_badges_data:
            if badge_record.get('roadmap_id') == selected_roadmap_int:
                status = badge_record.get('status', '').lower().strip()

                if status in completed_statuses:
                    completed_count += 1
                elif status and status not in excluded_statuses:
                    in_progress_count += 1

        # For pre-production resources, count missing required badges as in-progress
        for resource_id, resource_data in pivot_data.items():

            # Get badge IDs this resource already has records for
            existing_badge_ids = set(resource_data.get('badge_statuses', {}).keys())

            # Get verified badge IDs for this resource 
            verified_badge_ids = {
                badge_id for badge_id, status in resource_data.get('badge_statuses', {}).items()
                if status and status.lower().strip() in completed_statuses
            }

            # Find required badges that are either missing or not verified
            non_verified_required = required_badge_ids - verified_badge_ids

            # Count them as in-progress (but don't double-count ones already in records)
            missing_required = non_verified_required - existing_badge_ids
            in_progress_count += len(missing_required)

        return completed_count, in_progress_count


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_roadmap = self.request.GET.get('roadmap')

        # Fetch all data
        roadmaps_data = self.fetch_api_data('roadmaps')
        resources_data = self.fetch_api_data('resources')
        resource_roadmap_badges_data = self.fetch_api_data('resource_roadmap_badges')

        # DEBUG
        # print(f"\nData Fetch: Roadmaps={len(roadmaps_data)} | Resources={len(resources_data)} | Badges={len(resource_roadmap_badges_data)}")

        # Get pre-production resources grouped by roadmap
        preproduction_by_roadmap = self.get_preproduction_resources(
            resources_data, 
            resource_roadmap_badges_data,
            roadmaps_data
        )

        # Filter roadmaps (exclude drafts)
        roadmaps = [{
            'roadmap_id': rm.get('roadmap_id') or rm.get('id'),
            'name': rm.get('name', 'Unknown Roadmap')
        } for rm in roadmaps_data if rm.get('status', '').lower() != 'draft']

        # Fetch badges
        badges_data = self.fetch_api_data('badges')

        # Re-fetch filtered data if roadmap selected
        if selected_roadmap:
            try:
                roadmap_int = int(selected_roadmap)
                resource_roadmap_badges_data = self.fetch_api_data('resource_roadmap_badges', {'roadmap_id': roadmap_int})
            except (ValueError, TypeError):
                pass

        # Build lookups
        badge_lookup, resource_lookup = self.build_lookups(badges_data, resources_data)

        # Process roadmap data
        pivot_data, resources_without_badges = self.process_roadmap_data(
            selected_roadmap, 
            resource_roadmap_badges_data, 
            badge_lookup, 
            resource_lookup, 
            resources_data,
            preproduction_by_roadmap
        )

        # Get selected roadmap as int
        try:
            selected_roadmap_int = int(selected_roadmap)
        except (ValueError, TypeError):
            selected_roadmap_int = None

        # Build badges list
        badges_list = []
        seen_badges = {}

        roadmap_badges_data = self.fetch_roadmap_badges_data(selected_roadmap)

        # Calculate percentages
        verified_count = 0
        completed_statuses = {'verified', 'available', 'approved', 'complete', 'completed'}

        for badge_record in resource_roadmap_badges_data:
            if (str(badge_record.get('roadmap_id')) == str(selected_roadmap) and
                str(badge_record.get('badge_id')) in [str(b.get('badge_id')) for b in roadmap_badges_data if b.get('required', False)] and
                badge_record.get('status', '').lower().strip() in completed_statuses):
                verified_count += 1

        completed_badges, in_progress_badges = self.calculate_badge_status_counts(
            selected_roadmap,
            resource_roadmap_badges_data,
            roadmap_badges_data,
            pivot_data
        )

        # potential completions
        potential_total = len(pivot_data) * len([b for b in roadmap_badges_data if b.get('required', False)])
        potential_percentage = round((verified_count / potential_total) * 100, 1) if potential_total > 0 else 0


        # Build badges list from roadmap badges
        for badge_record in roadmap_badges_data:
            badge_id = badge_record.get('badge_id')

            # Skip invalid badge IDs
            if badge_id is None:
                continue

            badge_id_str = str(badge_id)
            badge_name = badge_lookup.get(badge_id_str, f'Badge {badge_id_str}')

            if badge_id_str not in seen_badges:
                seen_badges[badge_id_str] = {
                    'id': badge_id_str,
                    'badge': {'name': badge_name},
                    'required': badge_record.get('required', False)
                }
            elif badge_record.get('required', False):
                seen_badges[badge_id_str]['required'] = True

        # Add badges from resource badge records
        for badge_record in resource_roadmap_badges_data:
            if badge_record.get('roadmap_id') == selected_roadmap_int:
                badge_id = badge_record.get('badge_id')

                # Skip invalid badge IDs (explicit None check)
                if badge_id is None:
                    continue

                badge_id_str = str(badge_id)
                badge_name = badge_lookup.get(badge_id_str, f'Badge {badge_id_str}')

                if badge_id_str not in seen_badges:
                    seen_badges[badge_id_str] = {
                        'id': badge_id_str,
                        'badge': {'name': badge_name},
                        'required': False
                    }

        # Sort badges list
        badges_list = sorted(list(seen_badges.values()), 
                key=lambda x: (not x['required'], x['badge']['name']))

        # Update context
        context.update({
            'roadmaps': roadmaps,
            'selected_roadmap': int(selected_roadmap) if selected_roadmap else None,
            'pivot_data': pivot_data,
            'badges_list': badges_list,
            # 'required_percentage': required_percentage,
            'verified_required_count': verified_count,
            # 'total_required_count': total_count,
            'completed_badges': completed_badges,
            'in_progress_badges': in_progress_badges,
            'preproduction_by_roadmap': preproduction_by_roadmap,
            'potential_required_total': potential_total,
            'potential_percentage': potential_percentage,
        })

        return context


    def dispatch(self, request, *args, **kwargs):
        # Default roadmap
        if not request.GET.get('roadmap'):
            return redirect(f'{request.path}?roadmap={self.DEFAULT_ROADMAP}')
        return super().dispatch(request, *args, **kwargs)
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from drf_spectacular.utils import extend_schema, OpenApiParameter
from ..serializers import ResourcePivotResponseSerializer, GroupPivotResponseSerializer


class RoadmapResourceBadgesAPI(GenericAPIView):
    """JSON API endpoint for resource badge status"""
    permission_classes = [AllowAny]
    renderer_classes = [JSONRenderer]

    @extend_schema(
        operation_id='resource_pivot_json',
        description='Get resource badge status data grouped by roadmap',
        parameters=[
            OpenApiParameter(
                name='roadmap',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Roadmap ID',
                required=False
            )
        ],
        responses={200: ResourcePivotResponseSerializer}
    )
    def get(self, request):
        view = RoadmapResourceBadgesView()
        view.request = request._request
        view.kwargs = {}

        roadmap = request.GET.get('roadmap', RoadmapResourceBadgesView.DEFAULT_ROADMAP)

        from django.http import QueryDict
        new_get = QueryDict('', mutable=True)
        new_get.update(view.request.GET)
        new_get['roadmap'] = str(roadmap)
        view.request.GET = new_get

        context = view.get_context_data()

        return Response({
            'roadmaps': context.get('roadmaps', []),
            'selected_roadmap': context.get('selected_roadmap'),
            'pivot_data': context.get('pivot_data', {}),
            'badges_list': context.get('badges_list', []),
            'completed_badges': context.get('completed_badges', 0),
            'in_progress_badges': context.get('in_progress_badges', 0),
            'verified_required_count': context.get('verified_required_count', 0),
            'potential_required_total': context.get('potential_required_total', 0),
            'potential_percentage': context.get('potential_percentage', 0),
            'preproduction_by_roadmap': context.get('preproduction_by_roadmap', {}),
        })

