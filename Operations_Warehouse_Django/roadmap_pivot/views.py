from django.conf import settings
from django.views.generic import TemplateView
from django.shortcuts import redirect
import requests

class RoadmapResourceBadgesView(TemplateView):
    template_name = 'roadmap_pivot/roadmap_resource_pivot.html'
    DEFAULT_ROADMAP = 67

    @property
    def API_BASE(self):
        # Lazy load API URL - check cache first
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

    @property
    def FALLBACK_API_BASE(self):
        # Production fallback for dev only
        from Operations_Warehouse_Django.settings import CONF
        return ("https://operations-api.access-ci.org/wh2/integration_badges/v1" 
                if CONF.get('DEBUG', False) else None)

    def fetch_api_data(self, endpoint):
        # Try local first, fallback to prod if empty/failed
        def try_endpoint(base_url):
            response = requests.get(f"{base_url}/{endpoint}/", timeout=30)
            response.raise_for_status()
            return response.json().get('results', [])

        try:
            data = try_endpoint(self.API_BASE)
            # If empty and fallback exists, try prod
            if not data and self.FALLBACK_API_BASE:
                data = try_endpoint(self.FALLBACK_API_BASE)
            return data
        except Exception:
            # Last resort: try fallback if available
            if self.FALLBACK_API_BASE:
                try:
                    return try_endpoint(self.FALLBACK_API_BASE)
                except Exception:
                    pass
            return []

    def build_lookups(self, badges_data, resources_data):
        # Quick lookups for badges and resources
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

        # Get unique statuses and resources with badges
        status_columns = sorted({item.get('status') for item in roadmap_badges if item.get('status')})
        resource_ids_with_badges = {str(item.get('info_resourceid')) for item in roadmap_badges 
                                  if item.get('info_resourceid')}

        # Build pivot table
        pivot_data = {}
        for resource_id in sorted(resource_ids_with_badges):
            resource_info = resource_lookup.get(resource_id, {
                'info_resourceid': resource_id,
                'resource_descriptive_name': f'Resource {resource_id}'
            })

            # Group badges by status for this resource
            resource_badges = [item for item in roadmap_badges 
                             if str(item.get('info_resourceid')) == resource_id]

            status_data = {}
            for status in status_columns:
                badges_for_status = []
                for rb in resource_badges:
                    if rb.get('status') == status:
                        badge_id = rb.get('badge_id')
                        badges_for_status.append({
                            'badge': {'name': badge_lookup.get(str(badge_id), f"Badge {badge_id}")},
                            'status': status,
                            'comment': rb.get('comment', ''),
                            'status_updated_by': rb.get('status_updated_by', ''),
                            'badge_access_url': rb.get('badge_access_url', ''),
                            'badge_access_url_label': rb.get('badge_access_url_label', '')
                        })

                badges_for_status.sort(key=lambda x: x['badge']['name'])
                status_data[status] = badges_for_status

            pivot_data[resource_id] = {
                'resource_info': resource_info,
                'status_data': status_data
            }

        # Count badges per status
        status_counts = {status: len([item for item in roadmap_badges if item.get('status') == status])
                        for status in status_columns}

        # Find resources without any badges
        all_resource_ids = {str(res.get('info_resourceid') or res.get('resource_id'))
                           for res in resources_data 
                           if res.get('info_resourceid') or res.get('resource_id')}

        resources_without_badges = [
            resource_lookup.get(resource_id, {
                'info_resourceid': resource_id,
                'resource_descriptive_name': f'Resource {resource_id}'
            })
            for resource_id in sorted(all_resource_ids - resource_ids_with_badges)
        ]

        return pivot_data, status_counts, resources_without_badges, status_columns

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_roadmap = self.request.GET.get('roadmap')

        # # DEBUG: database info
        # from django.db import connection
        # context['debug_info'] = {
        #     'database_name': connection.settings_dict['NAME'],
        #     'database_host': connection.settings_dict['HOST'],
        #     'database_port': connection.settings_dict['PORT'],
        #     'api_base_used': self.API_BASE,
        #     'fallback_available': bool(self.FALLBACK_API_BASE),
        # }

        # Fetch all data in parallel
        endpoints = ['roadmaps', 'badges', 'resources', 'resource_roadmap_badges']
        roadmaps_data, badges_data, resources_data, resource_roadmap_badges_data = [
            self.fetch_api_data(endpoint) for endpoint in endpoints
        ]

        # Build roadmaps dropdown
        roadmaps = [{
            'roadmap_id': rm.get('roadmap_id') or rm.get('id'),
            'name': rm.get('name', 'Unknown Roadmap')
        } for rm in roadmaps_data]

        # Process everything
        badge_lookup, resource_lookup = self.build_lookups(badges_data, resources_data)
        pivot_data, status_counts, resources_without_badges, status_columns = self.process_roadmap_data(
            selected_roadmap, resource_roadmap_badges_data, badge_lookup, resource_lookup, resources_data
        )

        context.update({
            'roadmaps': roadmaps,
            'selected_roadmap': int(selected_roadmap) if selected_roadmap else None,
            'status_columns': status_columns,
            'pivot_data': pivot_data,
            'resources_without_badges': {'count': len(resources_without_badges), 'list': resources_without_badges},
            'status_counts': status_counts,
        })

        return context

    def dispatch(self, request, *args, **kwargs):
        # Redirect to default roadmap if none selected
        if not request.GET.get('roadmap'):
            return redirect(f'{request.path}?roadmap={self.DEFAULT_ROADMAP}')
        return super().dispatch(request, *args, **kwargs)
