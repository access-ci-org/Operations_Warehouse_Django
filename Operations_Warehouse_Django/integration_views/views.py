# used Claude 4 Code to assist in this code and verified against docs and other examples from the web. No inappropriate data was shared in the process
from django.conf import settings
from django.views.generic import TemplateView
from django.shortcuts import redirect
import requests
from datetime import datetime
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from collections import defaultdict


@method_decorator(cache_page(60 * 5), name='get')
class RoadmapResourceBadgesView(TemplateView):
    template_name = 'integration_views/resource_pivot.html'
    DEFAULT_ROADMAP = 67

    @property
    def API_BASE(self):
        if hasattr(self, '_api_base'):
            return self._api_base

        from Operations_Warehouse_Django.settings import CONF

        self._api_base = CONF.get('INTEGRATION_BADGES_API_BASE')
        if not self._api_base:
            base = CONF.get('API_BASE', '/wh2')
            self._api_base = (f"{base}/integration_badges/v1" if base.startswith('http') 
                            else f"http://localhost:8000{base}/integration_badges/v1")
        return self._api_base

    def fetch_api_data(self, endpoint, params=None):
        """Fetch API data with optional query parameters for filtering"""
        def try_endpoint(base_url):
            url = f"{base_url}/{endpoint}/"
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json().get('results', [])

        production_api = "https://operations-api.access-ci.org/wh2/integration_badges/v1"

        try:
            data = try_endpoint(production_api)
            return data
        except Exception:
            try:
                data = try_endpoint(self.API_BASE)
                return data
            except Exception:
                return []

    def build_lookups(self, badges_data, resources_data):
        badge_lookup = {
            str(badge.get('id') or badge.get('badge_id')): badge.get('name', 'Unknown Badge')
            for badge in badges_data if badge.get('id') or badge.get('badge_id')
        }

        resource_lookup = {
            str(res.get('info_resourceid') or res.get('resource_id')): res
            for res in resources_data if res.get('info_resourceid') or res.get('resource_id')
        }

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

        resource_ids_with_badges = {str(item.get('info_resourceid')) for item in roadmap_badges 
                                if item.get('info_resourceid')}

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
        preproduction_statuses = ['pre-production', 'coming soon']

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

        resource_to_roadmap = {}
        for badge_record in resource_roadmap_badges_data:
            resource_id = str(badge_record.get('info_resourceid'))
            roadmap_id = badge_record.get('roadmap_id')
            if resource_id and roadmap_id:
                resource_to_roadmap[resource_id] = roadmap_id

        preproduction_by_roadmap = {}

        for res in resources_data:
            resource_id = str(res.get('info_resourceid') or res.get('resource_id'))
            fixed_status = res.get('fixed_status', '').lower().strip()
            latest_status = res.get('latest_status', '').lower().strip()

            if (fixed_status in preproduction_statuses or 
                latest_status in preproduction_statuses or
                'pre-production' in fixed_status or
                'coming soon' in fixed_status or
                'pre-production' in latest_status or
                'coming soon' in latest_status):

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

    def calculate_badge_status_counts(self, selected_roadmap, resource_roadmap_badges_data):
        """Count completed and in-progress badges for all resources"""
        try:
            selected_roadmap_int = int(selected_roadmap)
        except (ValueError, TypeError):
            return 0, 0

        completed_count = 0
        in_progress_count = 0

        completed_statuses = {'verified', 'tasks-completed', 'complete', 'completed'}
        excluded_statuses = {'not planned', 'not-planned', ''}

        for badge_record in resource_roadmap_badges_data:
            if badge_record.get('roadmap_id') == selected_roadmap_int:
                status = badge_record.get('status', '').lower().strip()

                if status in completed_statuses:
                    completed_count += 1
                elif status and status not in excluded_statuses:
                    in_progress_count += 1

        return completed_count, in_progress_count

    def calculate_required_badge_percentage(self, selected_roadmap, roadmap_badges_data, resource_roadmap_badges_data):
        """Calculate percentage of required badges that are verified"""
        try:
            selected_roadmap_int = int(selected_roadmap)
        except (ValueError, TypeError):
            return 0, 0, 0

        required_badge_ids = set()
        for badge_record in roadmap_badges_data:
            if badge_record.get('required', False):
                badge_info = badge_record.get('badge', {})
                badge_id = str(badge_info.get('badge_id'))
                required_badge_ids.add(badge_id)

        if not required_badge_ids:
            return 100, 0, 0

        verified_required_count = 0
        total_required_instances = 0

        for badge_record in resource_roadmap_badges_data:
            if (badge_record.get('roadmap_id') == selected_roadmap_int and 
                str(badge_record.get('badge_id')) in required_badge_ids):
                total_required_instances += 1
                if badge_record.get('status') == 'verified':
                    verified_required_count += 1

        if total_required_instances == 0:
            return 0, 0, 0

        percentage = round((verified_required_count / total_required_instances) * 100, 1)
        return percentage, verified_required_count, total_required_instances

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_roadmap = self.request.GET.get('roadmap')

        roadmaps_data = self.fetch_api_data('roadmaps')
        resources_data = self.fetch_api_data('resources')
        resource_roadmap_badges_data = self.fetch_api_data('resource_roadmap_badges')

        preproduction_by_roadmap = self.get_preproduction_resources(
            resources_data, 
            resource_roadmap_badges_data,
            roadmaps_data
        )

        roadmaps = [{
            'roadmap_id': rm.get('roadmap_id') or rm.get('id'),
            'name': rm.get('name', 'Unknown Roadmap')
        } for rm in roadmaps_data
            if rm.get('status', '').lower() != 'draft'
            ]

        badges_data = self.fetch_api_data('badges')

        if selected_roadmap:
            try:
                roadmap_int = int(selected_roadmap)
                resource_roadmap_badges_data = self.fetch_api_data('resource_roadmap_badges', {'roadmap_id': roadmap_int})
            except (ValueError, TypeError):
                pass

        badge_lookup, resource_lookup = self.build_lookups(badges_data, resources_data)

        pivot_data, resources_without_badges = self.process_roadmap_data(
            selected_roadmap, 
            resource_roadmap_badges_data, 
            badge_lookup, 
            resource_lookup, 
            resources_data,
            preproduction_by_roadmap
        )

        try:
            selected_roadmap_int = int(selected_roadmap)
        except (ValueError, TypeError):
            selected_roadmap_int = None

        badges_list = []
        seen_badges = {}

        roadmap_badges_data = self.fetch_roadmap_badges_data(selected_roadmap)

        required_percentage, verified_count, total_count = self.calculate_required_badge_percentage(
            selected_roadmap,
            roadmap_badges_data,
            resource_roadmap_badges_data
        )

        completed_badges, in_progress_badges = self.calculate_badge_status_counts(
            selected_roadmap,
            resource_roadmap_badges_data
        )

        for badge_record in roadmap_badges_data:
            badge_info = badge_record.get('badge', {})
            badge_id = str(badge_info.get('badge_id'))
            badge_name = badge_info.get('name', f'Badge {badge_id}')
            is_required = badge_record.get('required', False)

            if badge_id not in seen_badges:
                seen_badges[badge_id] = {
                    'id': badge_id,
                    'badge': {'name': badge_name},
                    'required': is_required
                }
            else:
                if is_required:
                    seen_badges[badge_id]['required'] = True

        for badge_record in resource_roadmap_badges_data:
            if badge_record.get('roadmap_id') == selected_roadmap_int:
                badge_id = str(badge_record.get('badge_id'))
                badge_name = badge_lookup.get(badge_id, f'Badge {badge_id}')

                if badge_id not in seen_badges:
                    seen_badges[badge_id] = {
                        'id': badge_id,
                        'badge': {'name': badge_name},
                        'required': False
                    }

        badges_list = sorted(list(seen_badges.values()), 
                key=lambda x: (not x['required'], x['badge']['name']))

        context.update({
            'roadmaps': roadmaps,
            'selected_roadmap': int(selected_roadmap) if selected_roadmap else None,
            'pivot_data': pivot_data,
            'badges_list': badges_list,
            'required_percentage': required_percentage,
            'verified_required_count': verified_count,
            'total_required_count': total_count,
            'completed_badges': completed_badges,
            'in_progress_badges': in_progress_badges,
            'preproduction_by_roadmap': preproduction_by_roadmap,
        })

        return context

    def dispatch(self, request, *args, **kwargs):
        # Default roadmap redirect - ONLY for RoadmapResourceBadgesView
        if not request.GET.get('roadmap'):
            return redirect(f'{request.path}?roadmap={self.DEFAULT_ROADMAP}')
        return super().dispatch(request, *args, **kwargs)


@method_decorator(cache_page(60 * 5), name='get')
class GroupBadgeStatusView(TemplateView):
    """Group-level badge aggregation view - NO roadmaps"""
    template_name = 'integration_views/group_pivot.html'

    def fetch_api_data(self, endpoint, params=None):
        """Fetch data from API endpoints"""
        base_url = 'https://operations-api.access-ci.org/wh2'
        endpoints = {
            'groups': f'{base_url}/cider/v1/access-active-groups/',
            'resource_roadmap_badges': f'{base_url}/integration_badges/v1/resource_roadmap_badges/',
            'roadmap_badges': f'{base_url}/integration_badges/v1/roadmap_badges_by_roadmap/', 
        }

        url = endpoints.get(endpoint, endpoint)

        print(f"Fetching: {url}")

        try:
            response = requests.get(url, params={'format': 'json', **(params or {})}, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Handle different API response formats
            if isinstance(data, list):
                result = data
            elif isinstance(data, dict):
                # For groups endpoint, extract the groups list
                if endpoint == 'groups' and 'active_groups' in data:
                    result = data['active_groups']
                else:
                    result = data.get('results', data.get('data', []))
            else:
                result = []

            # DEBUG
            # print(f"Got {len(result)} items from {endpoint}")
            # if result and isinstance(result, list):
            #     print(f"First item type: {type(result[0])}")

            return result
        except requests.RequestException as e:
            print(f"Error: {e}")
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

            # Get the roadmap(s) this resource belongs to
            resource_roadmap_id = resource_to_roadmap.get(resource_id)

            # Get badges only from this resource's roadmap
            if resource_roadmap_id and resource_roadmap_id in roadmap_badges_by_roadmap:
                relevant_badge_ids = roadmap_badges_by_roadmap[resource_roadmap_id]
            else:
                relevant_badge_ids = set()  # No roadmap = no expected badges

            # Count badges with explicit statuses
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

            # Count badges missing from this resource's SPECIFIC roadmap
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

        # Fetch roadmap badges, keeping them separated by roadmap
        roadmap_badges_by_roadmap = defaultdict(set)
        all_required_badge_ids = set()

        try:
            roadmaps_response = requests.get(
                'https://operations-api.access-ci.org/wh2/integration_badges/v1/roadmaps/',
                params={'format': 'json'},
                timeout=30
            )
            roadmaps_response.raise_for_status()
            roadmaps = roadmaps_response.json().get('results', [])

            for roadmap in roadmaps:
                roadmap_id = roadmap.get('roadmap_id') or roadmap.get('id')
                if 'badges' in roadmap:
                    for badge_record in roadmap['badges']:
                        badge = badge_record.get('badge')
                        if isinstance(badge, dict):
                            badge_id = str(badge.get('badge_id'))
                        elif badge:
                            badge_id = str(badge)
                        else:
                            continue

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
        preproduction_keywords = ['coming soon', 'pre-production', 'preproduction']

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





