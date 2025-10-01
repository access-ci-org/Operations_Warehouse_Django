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
    template_name = 'roadmap_pivot/roadmap_resource_pivot.html'
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

    def process_roadmap_data(self, selected_roadmap, resource_roadmap_badges_data, badge_lookup, resource_lookup, resources_data):
        # Process and pivot data for the selected roadmap
        try:
            selected_roadmap_int = int(selected_roadmap)
        except (ValueError, TypeError):
            return {}, {}, [], []

        # Filter to selected roadmap only
        roadmap_badges = [item for item in resource_roadmap_badges_data 
                         if item.get('roadmap_id') == selected_roadmap_int]

        # Get resource IDs that exist in BOTH badge data AND resources API
        resource_ids_with_badges = {str(item.get('info_resourceid')) for item in roadmap_badges 
                                  if item.get('info_resourceid')}

        # FILTER: Only keep resources that exist in the resources API
        valid_resource_ids = {resource_id for resource_id in resource_ids_with_badges 
                             if resource_id in resource_lookup}

        # Build pivot table - only for valid resources
        pivot_data = {}
        for resource_id in valid_resource_ids:
            resource_info = resource_lookup[resource_id]

            # Group badges by status for this resource
            resource_badges = [item for item in roadmap_badges 
                             if str(item.get('info_resourceid')) == resource_id]

            badge_statuses = {}
            for rb in resource_badges:
                badge_id = rb.get('badge_id')
                badge_statuses[str(badge_id)] = rb.get('status')

            # Parse date
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
                'latest_status_begin': latest_status_begin_date
            }

        # Sort pivot_data by resource_descriptive_name
        pivot_data = dict(sorted(pivot_data.items(), 
                               key=lambda x: x[1]['resource_info'].get('resource_descriptive_name', '').lower()))

        # Find resources without any badges (only from valid resources)
        all_valid_resource_ids = {str(res.get('info_resourceid') or res.get('resource_id'))
                                 for res in resources_data 
                                 if res.get('info_resourceid') or res.get('resource_id')}

        resources_without_badges = [
            resource_lookup[resource_id]
            for resource_id in sorted(all_valid_resource_ids - valid_resource_ids)
            if resource_id in resource_lookup
        ]

        return pivot_data, resources_without_badges

    def get_preproduction_resources(self, resources_data, resource_roadmap_badges_data):
        """Get all pre-production resources (pre-production, coming soon, etc.) - excludes post-production"""
        # Define pre-production statuses (excludes post-production)
        preproduction_statuses = ['pre-production', 'coming soon']

        # Filter pre-production resources
        preproduction_resources = []
        for res in resources_data:
            resource_id = str(res.get('info_resourceid') or res.get('resource_id'))

            # Flexible status matching
            fixed_status = res.get('fixed_status', '').lower().strip()
            latest_status = res.get('latest_status', '').lower().strip()

            # Check both fields and be flexible with matching
            if (fixed_status in preproduction_statuses or 
                latest_status in preproduction_statuses or
                'pre-production' in fixed_status or
                'coming soon' in fixed_status or
                'pre-production' in latest_status or
                'coming soon' in latest_status):

                # Parse date
                latest_status_begin_str = res.get('latest_status_begin')
                latest_status_begin_date = None

                if latest_status_begin_str:
                    try:
                        latest_status_begin_date = datetime.strptime(latest_status_begin_str, '%Y-%m-%d').date()
                    except (ValueError, TypeError):
                        latest_status_begin_date = None

                preproduction_resources.append({
                    'resource_info': res,
                    'fixed_status': res.get('fixed_status'),
                    'latest_status_begin': latest_status_begin_date
                })

        return sorted(preproduction_resources, 
                     key=lambda x: (x['fixed_status'], x['resource_info'].get('resource_descriptive_name', '')))

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

    def calculate_required_badge_percentage(self, selected_roadmap, roadmap_badges_data, resource_roadmap_badges_data):
        """Calculate percentage of required badges that are verified"""
        try:
            selected_roadmap_int = int(selected_roadmap)
        except (ValueError, TypeError):
            return 0

        # Get required badge IDs from roadmap definition
        required_badge_ids = set()
        for badge_record in roadmap_badges_data:
            if badge_record.get('required', False):
                badge_info = badge_record.get('badge', {})
                badge_id = str(badge_info.get('badge_id'))
                required_badge_ids.add(badge_id)

        if not required_badge_ids:
            return 100  

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
            return 0

        return round((verified_required_count / total_required_instances) * 100, 1)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_roadmap = self.request.GET.get('roadmap')

        # Always fetch roadmaps & resources (needed by both tabs)
        roadmaps_data = self.fetch_api_data('roadmaps')
        resources_data = self.fetch_api_data('resources')

        # Build roadmaps tabs & Pre-Production tab
        roadmaps = [{
            'roadmap_id': rm.get('roadmap_id') or rm.get('id'),
            'name': rm.get('name', 'Unknown Roadmap')
        } for rm in roadmaps_data]

        # Add Pre-Production tab
        roadmaps.append({
            'roadmap_id': 'preproduction',
            'name': 'Pre-Production Resources'
        })

        # CONDITIONAL API LOADING - This is the key optimization
        if selected_roadmap == 'preproduction':
            # Pre-production: Only needs resources_data (already fetched)
            preproduction_resources = self.get_preproduction_resources(resources_data, [])
            context.update({
                'roadmaps': roadmaps,
                'selected_roadmap': selected_roadmap,
                'is_preproduction_tab': True,
                'preproduction_resources': preproduction_resources,
                'pivot_data': {},
                'badges_list': [],
            })
        else:
            # Regular roadmaps: Fetch badges and badge data only when needed
            badges_data = self.fetch_api_data('badges')

            # Filter resource_roadmap_badges to selected roadmap if possible
            if selected_roadmap:
                try:
                    roadmap_int = int(selected_roadmap)
                    resource_roadmap_badges_data = self.fetch_api_data('resource_roadmap_badges', {'roadmap_id': roadmap_int})
                except (ValueError, TypeError):
                    resource_roadmap_badges_data = self.fetch_api_data('resource_roadmap_badges')
            else:
                resource_roadmap_badges_data = self.fetch_api_data('resource_roadmap_badges')

            # Process everything (only for regular roadmaps)
            badge_lookup, resource_lookup = self.build_lookups(badges_data, resources_data)

            pivot_data, resources_without_badges = self.process_roadmap_data(
                selected_roadmap, resource_roadmap_badges_data, badge_lookup, resource_lookup, resources_data
            )


            # badges_list from badges_data
            try:
                selected_roadmap_int = int(selected_roadmap)
            except (ValueError, TypeError):
                selected_roadmap_int = None

            badges_list = []
            seen_badges = {}

            # Get badges from resource_roadmap_badges_data for each specific roadmap
            roadmap_badges_data = self.fetch_roadmap_badges_data(selected_roadmap)

            # Calculate required badge completion percentage
            required_percentage = self.calculate_required_badge_percentage(
                selected_roadmap, roadmap_badges_data, resource_roadmap_badges_data
            )

            # Build badges list 
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

            # Also add any badges from resource data that might not be in roadmap definition
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

            # Convert to list and sort alphabetically
            badges_list = sorted(list(seen_badges.values()), 
                    key=lambda x: (not x['required'], x['badge']['name']))

            context.update({
                'roadmaps': roadmaps,
                'selected_roadmap': int(selected_roadmap) if selected_roadmap else None,
                'is_preproduction_tab': False,
                'pivot_data': pivot_data,
                'badges_list': badges_list,
                'required_percentage': required_percentage,
            })

        return context


    def dispatch(self, request, *args, **kwargs):
        # Default roadmap
        if not request.GET.get('roadmap'):
            return redirect(f'{request.path}?roadmap={self.DEFAULT_ROADMAP}')
        return super().dispatch(request, *args, **kwargs)
