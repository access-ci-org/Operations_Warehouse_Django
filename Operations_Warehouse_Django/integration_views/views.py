# used Claude 4 Code to assist in this code and verified against docs and other examples from the web. No inappropriate data was shared in the process
from django.conf import settings
from django.views.generic import TemplateView
from django.shortcuts import redirect
import requests
from datetime import datetime
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

@method_decorator(cache_page(60 * 5), name='get')  # Caching
class RoadmapResourceBadgesView(TemplateView):
    template_name = 'integration_views/resource_pivot.html'
    DEFAULT_ROADMAP = 67

    @property
    def API_BASE(self):
        if hasattr(self, '_api_base'):
            return self._api_base

        from Operations_Warehouse_Django.settings import CONF

        # Try specific integration API first, then build from base
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
        # lookups for badges and resources
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

        # Get pre-production resource IDs for this roadmap
        preproduction_resource_ids = set()
        if selected_roadmap_int in preproduction_by_roadmap:
            preproduction_resource_ids = {
                str(res['resource_info'].get('info_resourceid') or res['resource_info'].get('resource_id'))
                for res in preproduction_by_roadmap[selected_roadmap_int]
            }

        # Filter to selected roadmap only
        roadmap_badges = [item for item in resource_roadmap_badges_data 
                        if item.get('roadmap_id') == selected_roadmap_int]

        resource_ids_with_badges = {str(item.get('info_resourceid')) for item in roadmap_badges 
                                if item.get('info_resourceid')}

        # Combine: resources with badges + pre-production resources
        all_resource_ids = resource_ids_with_badges | preproduction_resource_ids

        valid_resource_ids = {resource_id for resource_id in all_resource_ids 
                            if resource_id in resource_lookup}

        # Build pivot table
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

            # Build cider_type -> roadmap_id mapping
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

            # Build resource_id -> roadmap_id from badge data (for resources WITH badges)
            resource_to_roadmap = {}
            for badge_record in resource_roadmap_badges_data:
                resource_id = str(badge_record.get('info_resourceid'))
                roadmap_id = badge_record.get('roadmap_id')
                if resource_id and roadmap_id:
                    resource_to_roadmap[resource_id] = roadmap_id

            # Group pre-production resources by roadmap
            preproduction_by_roadmap = {}

            for res in resources_data:
                resource_id = str(res.get('info_resourceid') or res.get('resource_id'))
                fixed_status = res.get('fixed_status', '').lower().strip()
                latest_status = res.get('latest_status', '').lower().strip()

                # Check if pre-production
                if (fixed_status in preproduction_statuses or 
                    latest_status in preproduction_statuses or
                    'pre-production' in fixed_status or
                    'coming soon' in fixed_status or
                    'pre-production' in latest_status or
                    'coming soon' in latest_status):

                    # Get roadmap_id: first try badge data, then fall back to cider_type
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

            # Sort each roadmap's resources
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

            # Check if roadmaps list already has badge info
            roadmaps_list = self.fetch_api_data('roadmaps')
            for roadmap in roadmaps_list:
                if roadmap.get('roadmap_id') == selected_roadmap_int:
                    if 'badges' in roadmap:
                        return roadmap.get('badges', [])
                    break

            return []
        except (ValueError, TypeError):
            return []

    # counts of badges
    def calculate_badge_status_counts(self, selected_roadmap, resource_roadmap_badges_data):
        """Count completed and in-progress badges for all resources (production + pre-production)"""
        try:
            selected_roadmap_int = int(selected_roadmap)
        except (ValueError, TypeError):
            return 0, 0

        completed_count = 0
        in_progress_count = 0

         # Statuses that indicate completion
        completed_statuses = {'verified', 'tasks-completed', 'tasls-completed', 'complete', 'completed'}

        # Statuses to exclude entirely
        excluded_statuses = {'not planned', 'not-planned', ''}

        for badge_record in resource_roadmap_badges_data:
            if badge_record.get('roadmap_id') == selected_roadmap_int:
                status = badge_record.get('status', '').lower().strip()

                if status in completed_statuses:
                    completed_count += 1
                elif status and status not in excluded_statuses:
                    # Count anything else with a status as in-progress
                    in_progress_count += 1

        return completed_count, in_progress_count
    
    # percentages of badges
    def calculate_required_badge_percentage(self, selected_roadmap, roadmap_badges_data, resource_roadmap_badges_data):
        """Calculate percentage of required badges that are verified and return counts"""
        try:
            selected_roadmap_int = int(selected_roadmap)
        except (ValueError, TypeError):
            return 0, 0, 0  # percentage, verified_count, total_count

        # Get required badge IDs from roadmap definition
        required_badge_ids = set()
        for badge_record in roadmap_badges_data:
            if badge_record.get('required', False):
                badge_info = badge_record.get('badge', {})
                badge_id = str(badge_info.get('badge_id'))
                required_badge_ids.add(badge_id)

        if not required_badge_ids:
            return 100, 0, 0  # All complete if no required badges

        # Count verified required badges from resource data
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

        # Always fetch roadmaps & resources
        roadmaps_data = self.fetch_api_data('roadmaps')
        resources_data = self.fetch_api_data('resources')
        resource_roadmap_badges_data = self.fetch_api_data('resource_roadmap_badges')

        # Get pre-production resources grouped by roadmap
        preproduction_by_roadmap = self.get_preproduction_resources(
            resources_data, 
            resource_roadmap_badges_data,
            roadmaps_data
        )

        # Build roadmaps tabs
        roadmaps = [{
            'roadmap_id': rm.get('roadmap_id') or rm.get('id'),
            'name': rm.get('name', 'Unknown Roadmap')
        } for rm in roadmaps_data
            if rm.get('status', '').lower() != 'draft'
            ]

        # Fetch badges and process
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

        # overall badge status counts
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
        
        # DEBUG: Find badges in data but not in badges_list
        badges_in_list = {b['id'] for b in badges_list}
        badges_in_data = {str(br.get('badge_id')) for br in resource_roadmap_badges_data 
                        if br.get('roadmap_id') == selected_roadmap_int}

        missing_badges = badges_in_data - badges_in_list
        if missing_badges:
            print(f"\n=== Missing badges for roadmap {selected_roadmap} ===")
            for badge_id in missing_badges:
                badge_name = badge_lookup.get(badge_id, f'Badge {badge_id}')
                print(f"  Badge ID {badge_id}: {badge_name}")
                # Count how many resources have this badge
                count = sum(1 for br in resource_roadmap_badges_data 
                        if str(br.get('badge_id')) == badge_id and br.get('roadmap_id') == selected_roadmap_int)
                print(f"    Used by {count} resources")
        # END of debug block

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
        # Default roadmap
        if not request.GET.get('roadmap'):
            return redirect(f'{request.path}?roadmap={self.DEFAULT_ROADMAP}')
        return super().dispatch(request, *args, **kwargs)
