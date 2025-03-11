from drf_spectacular.utils import OpenApiParameter, extend_schema
from itertools import chain
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework import status
from rest_framework.generics import GenericAPIView

from .models import *
from .filters import *
from .serializers import *
from .utils import cider_to_coco, mk_html_table

from warehouse_tools.exceptions import MyAPIException
from warehouse_tools.responses import MyAPIResponse, CustomPagePagination

# Create your views here.

class CiderInfrastructure_v1_ACCESSComputeCompare(GenericAPIView):
    '''
    Comparison of ACCESS Active Allocated Compute Resources
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    serializer_class = CiderInfrastructure_OtherAttrs_Serializer
    def get(self, request, format=None, **kwargs):
        returnformat = request.query_params.get('format' )
        objects = CiderInfrastructure_Active_Filter( type='Compute' )
        serializer = CiderInfrastructure_OtherAttrs_Serializer(objects, context={'request': request}, many=True)
        coco_data = cider_to_coco( { 'results': serializer.data } )
        if returnformat != 'json':
            coco_data = mk_html_table( coco_data )
        return MyAPIResponse( { 'results': coco_data }, template_name='coco.html' )

class CiderInfrastructure_v1_ACCESSContacts(GenericAPIView):
    '''
    ACCESS Active Resource Contacts
    '''
#    permission_classes = (IsAuthenticatedOrReadOnly,)
    permission_classes = (IsAuthenticated,)
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    serializer_class = CiderInfrastructure_ACCESSContacts_Serializer
    def get(self, request, format=None, **kwargs):
        returnformat = request.query_params.get('format' )
        objects1 = CiderInfrastructure_Active_Filter( type='Compute' )
        objects2 = CiderInfrastructure_Active_Filter( type='Storage' )
        all_contacts = {}
        for resource in chain(objects1, objects2):
            if not resource.protected_attributes or 'contacts' not in resource.protected_attributes:
                continue
            for contact in resource.protected_attributes['contacts']:
                for ct in contact['contact_types']:
                    if ct not in all_contacts:
                        all_contacts[ct] = set()
                    all_contacts[ct].add(f"{contact['name']} <{contact['email']}>")
        sorted_contacts = {}
        if returnformat == 'html':
            for key in sorted(all_contacts):
                sorted_contacts[key] = ', '.join(sorted(all_contacts[key]))
        else:
            for key in sorted(all_contacts):
                sorted_contacts[key] = sorted(all_contacts[key])
        return MyAPIResponse( { 'results': sorted_contacts }, template_name='contacts.html' )
    
class CiderInfrastructure_v1_ACCESSActiveList(GenericAPIView):
    '''
    ACCESS Active Allocated Compute and Storage Resources

    Returns: resource summary
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer)
    serializer_class = CiderInfrastructure_Summary_Serializer
    def get(self, request, format=None, **kwargs):
        if self.kwargs.get('info_groupid'):
            try:
                group = CiderGroups.objects.get(info_groupid=self.kwargs.get('info_groupid'))
            except (CiderGroups.DoesNotExist, CiderGroups.MultipleObjectsReturned):
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified info_groupid not found')
            objects = CiderInfrastructure_ActiveAllocated_Filter(affiliation='ACCESS', group_id=group.group_id, result='OBJECTS')
        else:
            objects = CiderInfrastructure_ActiveAllocated_Filter(affiliation='ACCESS', result='OBJECTS')
        sort_by = request.GET.get('sort')
        try:
            objects_sorted = objects.order_by(sort_by)
        except:
            objects_sorted = objects
        serializer = CiderInfrastructure_Summary_Serializer(objects_sorted, context={'request': request}, many=True)
        if request.accepted_renderer.format == 'html':
            return MyAPIResponse({'record_list': serializer.data}, template_name='list.html')
        return MyAPIResponse({'results': serializer.data})

class CiderInfrastructure_v2_ACCESSActiveList(GenericAPIView):
    '''
    ACCESS Active Allocated Compute and Storage Resources and Central Online Services Resources

    Returns: resource summary
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderInfrastructure_Summary_Serializer
    def get(self, request, format=None, **kwargs):
        objects1 = CiderInfrastructure_ActiveAllocated_Filter(affiliation='ACCESS', result='OBJECTS')
        objects2 = CiderInfrastructure_Active_Filter(affiliation='ACCESS', result='OBJECTS', type='Online Service')
        serializer = CiderInfrastructure_Summary_Serializer(chain(objects1, objects2), context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})

class CiderInfrastructure_v2_ACCESSAllList(GenericAPIView):
    '''
    ACCESS Active and Inactive Compute and Storage Resources and Central Online Services Resources

    Returns: resource summary
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderInfrastructure_Summary_Serializer
    def get(self, request, format=None, **kwargs):
        objects1 = CiderInfrastructure_All_Filter(affiliation='ACCESS', result='OBJECTS', type='Compute')
        objects2 = CiderInfrastructure_All_Filter(affiliation='ACCESS', result='OBJECTS', type='Storage')
        serializer = CiderInfrastructure_Summary_Serializer(chain(objects1, objects2), context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})
    
class CiderInfrastructure_v1_ACCESSAllocatedList(GenericAPIView):
    '''
    ACCESS Allocated Resources

    Returns: expanded summary
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderInfrastructure_Summary_Serializer
    def get(self, request, format=None, **kwargs):
        objects = CiderInfrastructure_ActiveAllocated_Filter(affiliation='ACCESS', result='OBJECTS')
        serializer = CiderInfrastructure_Summary_v2_Serializer(objects, context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})

class CiderInfrastructure_v1_ACCESSOnlineServicesList(GenericAPIView):
    '''
    ACCESS Active Online Services

    Returns: expanded summary
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderInfrastructure_Summary_Serializer
    def get(self, request, format=None, **kwargs):
        objects = CiderInfrastructure_Active_Filter(affiliation='ACCESS', result='OBJECTS', type='Online Service')
        serializer = CiderInfrastructure_Summary_v2_Serializer(objects, context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})

class CiderInfrastructure_v1_ACCESSScienceGatewaysList(GenericAPIView):
    '''
    ACCESS Active Science Gateways

    Returns: expanded summary
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderInfrastructure_Summary_Serializer
    @extend_schema(parameters=[
            OpenApiParameter('search', str, OpenApiParameter.QUERY),
            OpenApiParameter('page', int, OpenApiParameter.QUERY),
            OpenApiParameter('page_size', int, OpenApiParameter.QUERY)
        ])
    def get(self, request, format=None, **kwargs):
        arg_string = request.query_params.get('search')
        if arg_string:
            want_string = arg_string.lower()
        else:
            want_string = None
        try:
            page = request.GET.get('page')
            if page:
                page = int(page)
                if page == 0:
                    raise
        except:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Pagination page "{}" is not valid'.format(page))

        objects = CiderInfrastructure_Active_Filter(affiliation='ACCESS', result='OBJECTS', type='Science Gateway', search=want_string)
        
        if not page:
            serializer = CiderInfrastructure_Summary_v2_Gateway_Serializer(objects, context={'request': request}, many=True)
            return MyAPIResponse({'results': serializer.data})

        objects = objects.order_by('resource_descriptive_name')
        paginator = CustomPagePagination()
        query_page = paginator.paginate_queryset(objects, request, view=self)
        serializer = CiderInfrastructure_Summary_v2_Gateway_Serializer(query_page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data, request)

class CiderInfrastructure_v1_Detail(GenericAPIView):
    '''
    Generic Resource

    Returns: all resource detail
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (TemplateHTMLRenderer, JSONRenderer,)
    serializer_class = CiderInfrastructure_Detail_Serializer
    def get(self, request, format=None, **kwargs):
        # We need the base resource to pass to the serializer
        if self.kwargs.get('cider_resource_id'):        # Whether base or sub resource, grab the other one also
            try:
                item = CiderInfrastructure.objects.get(pk=self.kwargs['cider_resource_id'])
                if item.parent_resource: # Serializer wants the parent, but will serialize both
                    item =  CiderInfrastructure.objects.get(pk=item.parent_resource)
            except CiderInfrastructure.DoesNotExist:
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified cider_resource_id not found')
        elif self.kwargs.get('info_resourceid'):
            try:
                item = CiderInfrastructure.objects.get(info_resourceid=self.kwargs['info_resourceid'])
            except (CiderInfrastructure.DoesNotExist, CiderInfrastructure.MultipleObjectsReturned):
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified info_resourceid did not match a single resource')
        else:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Missing selection parameter')
        serializer = CiderInfrastructure_Detail_Serializer(item, context={'request': request})
        if request.accepted_renderer.format == 'html':
            return MyAPIResponse({'record_list': [serializer.data]}, template_name='detail.html')
        return MyAPIResponse({'results': serializer.data})

class CiderInfrastructure_v1_ACCESSActiveDetailList(GenericAPIView):
    '''
    ACCESS Active Resources

    Returns: all resource detail
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderInfrastructure_Detail_Serializer
    def get(self, request, format=None, **kwargs):
        if self.kwargs.get('info_groupid'):
            try:
                group = CiderGroups.objects.get(info_groupid=self.kwargs.get('info_groupid'))
            except (CiderGroups.DoesNotExist, CiderGroups.MultipleObjectsReturned):
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified info_groupid not found')
            objects = CiderInfrastructure_ActiveAllocated_Filter(affiliation='ACCESS', group_id=group.group_id, result='OBJECTS')
        else:
            objects = CiderInfrastructure_ActiveAllocated_Filter(affiliation='ACCESS', result='OBJECTS')
        serializer = CiderInfrastructure_Detail_Serializer(objects, context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})

class CiderInfrastructure_v1_Compute_Detail(GenericAPIView):
    '''
    Generic Compute Resource

    Returns: compute resource detail        
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderInfrastructure_Detail_Serializer
    def get(self, request, format=None, **kwargs):
        # We need the base resource to pass to the serializer
        if self.kwargs.get('cider_resource_id'):        # Whether base or sub resource, grab the other one also
            try:
                item = CiderInfrastructure.objects.get(pk=self.kwargs['cider_resource_id'])
                if item.cider_type != 'Compute':
                    raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified cider_resource_id is of a different type')
#                if item.parent_resource: # Serializer wants the parent, but will serialize both
#                    item =  CiderInfrastructure.objects.get(pk=item.parent_resource)
            except CiderInfrastructure.DoesNotExist:
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified cider_resource_id not found')
        else:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Missing selection parameter')
        serializer = CiderInfrastructure_Compute_Detail_Serializer(item, context={'request': request})
        return MyAPIResponse({'results': serializer.data})

class CiderFeatures_v1_Detail(GenericAPIView):
    '''
    A CiDeR Feature Categories
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderFeatures_Serializer
    def get(self, request, format=None, **kwargs):
        if not self.kwargs.get('category_id'):
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Missing selection parameter')
        try:
            item = CiderFeatures.objects.get(pk=self.kwargs['category_id'])
        except (CiderFeatures.DoesNotExist, CiderFeatures.MultipleObjectsReturned):
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified search failed')
        serializer = CiderFeatures_Serializer(item, context={'request': request})
        return MyAPIResponse({'results': serializer.data})

class CiderFeatures_v1_List(GenericAPIView):
    '''
    Selected CiDeR Feature Categories
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderFeatures_Serializer
    def get(self, request, format=None, **kwargs):
        try:
            items = objects = CiderFeatures.objects.all()
        except (CiderFeatures.DoesNotExist):
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified search failed')
        serializer = CiderFeatures_Serializer(items, context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})

# DENORMALIZE CODE THAT MAY BE USEFUL SOMEDAY
#        features = []
#        for category in items:
#            for feature in category.features:
#                key = '{}:{}'.format(category.feature_category_id, feature.get('id'))
#                features.append({
#                    **dict((k, getattr(category,k)) for k in ('feature_category_id', 'feature_category_name', 'feature_category_description')),
#                    **dict((k, feature.get(k)) for k in ('id', 'name', 'description'))
#                    })

class CiderGroups_v1_Detail(GenericAPIView):
    '''
    A CiDeR Group
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderGroups_Serializer
    def get(self, request, format=None, **kwargs):
        try:
            if self.kwargs.get('group_id'):
                item = CiderGroups.objects.get(pk=self.kwargs['group_id'])
            elif self.kwargs.get('info_groupid'):
                item = CiderGroups.objects.get(info_groupid=self.kwargs['info_groupid'])
            else:
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Missing query parameter')
        except (CiderGroups.DoesNotExist, CiderGroups.MultipleObjectsReturned):
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found or multiple found')
        serializer = CiderGroups_Serializer(item, context={'request': request})
        return MyAPIResponse({'results': serializer.data})

class CiderGroups_v1_List(GenericAPIView):
    '''
    Selected CiDeR Groups
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderGroups_Serializer
    def get(self, request, format=None, **kwargs):
        try:
            if self.kwargs.get('group_type'):
                items = CiderGroups.objects.filter(group_types__has_key=self.kwargs['group_type'])
            elif self.kwargs.get('info_resourceid'):
                items = CiderGroups.objects.filter(info_resourceids__has_key=self.kwargs['info_resourceid'])
            else:
                items = CiderGroups.objects.all()
        except (CiderGroups.DoesNotExist, CiderGroups.MultipleObjectsReturned):
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified search failed')
        serializer = CiderGroups_Serializer(items, context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})

class CiderOrganizations_v1_Detail(GenericAPIView):
    '''
    All CiDeR Organizations
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderOrganizations_Serializer
    def get(self, request, format=None, **kwargs):
        if not self.kwargs.get('organization_id'):
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Missing selection parameter')
        try:
            item = CiderOrganizations.objects.get(pk=self.kwargs['organization_id'])
        except (CiderOrganizations.DoesNotExist, CiderOrganizations.MultipleObjectsReturned):
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified search failed')
        serializer = CiderOrganizations_Serializer(item, context={'request': request})
        return MyAPIResponse({'results': serializer.data})

class CiderOrganizations_v1_List(GenericAPIView):
    '''
    Selected CiDeR Organization
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderOrganizations_Serializer
    def get(self, request, format=None, **kwargs):
        try:
            items = objects = CiderOrganizations.objects.all()
        except (CiderOrganizations.DoesNotExist):
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified search failed')
        serializer = CiderOrganizations_Serializer(items, context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})

# Design:
#   1st get all features
#   2nd get all ACCESS active resources
#   3rd get all or select groups
#       counting which resources are referenced in selected groups
#   4th count referenced orgs, features, and feature groups for referenced resources
class CiderACCESSActiveGroups_v1_List(GenericAPIView):
    '''
    ACCESS Active Compute and Storage Resource Groups
    
    Returns: Selected groups with active resources; per group resource id, feature, and org rollup; details about all referenced features, feature groups, and orgs
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderACCESSActiveGroups_v1_List_Serializer
    def get(self, request, format=None, **kwargs):
#       Default to all groups
#        if not self.kwargs.get('group_type') and not self.kwargs.get('group_id') and not self.kwargs.get('info_groupid'):
#            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Missing selection parameter')

        all_feature_categories = {}
        all_features = {}
        # The CiderFeatures model contains Feature Categories, and associated features in the features json field
        for feature_category in CiderFeatures.objects.all():
            # Key by id which are unique
            all_feature_categories[feature_category.feature_category_id] = {
                    'counter': 0,                           # For counting references
                    'feature_category_id': feature_category.feature_category_id,
                    'feature_category_name': feature_category.feature_category_name,
                    'feature_category_description': feature_category.feature_category_description
                }
            for feature in feature_category.features:
                # Key by id which are unique and are what resources reference
                all_features[feature['id']] = {
                        'counter': 0,                       # For counting references
                        'id': feature['id'],
                        'name': feature['name'],
                        'description': feature['description'],
                        'feature_category_id': feature_category.feature_category_id
                    }

        active_resources = {}
        active_orgs = {}
#       Expanding beyond Allocated Compute and Storage
#        resources = CiderInfrastructure_ActiveAllocated_Filter(affiliation='ACCESS', result='OBJECTS')
        resources = CiderInfrastructure_Active_Filter(affiliation='ACCESS', result='OBJECTS')
        for resource in resources:
            rid = resource.info_resourceid
            active_resources[rid] = {
                    'counter': 0,                             # For counting references in selected groups
                    'info_resourceid': rid,
                    'org_ids': [],
                    'feature_ids': []
                }
            if isinstance(resource.other_attributes.get('organizations'), list):
                for o in resource.other_attributes['organizations']:
                    oid = o.get('organization_id')
                    if not oid:
                        continue
                    active_resources[rid]['org_ids'].append(oid)
                    if oid not in active_orgs:
                        active_orgs[oid] = o
                        active_orgs[oid]['counter'] = 0     # For counting references in select group active resources
            if isinstance(resource.other_attributes.get('features'), list):
                for f in resource.other_attributes['features']:
                    fid = f.get('id')
                    if not fid:
                        continue
                    if fid not in all_features:
                        continue
                    active_resources[rid]['feature_ids'].append(fid)                          # All resource feature ids

        groups = []
        groups_extra = {}
        if self.kwargs.get('group_id'):
            query = CiderGroups.objects.filter(group_id=self.kwargs['group_id'])
        elif self.kwargs.get('info_groupid'):
            query = CiderGroups.objects.filter(info_groupid=self.kwargs['info_groupid'])
        elif self.kwargs.get('group_type'):
            query = CiderGroups.objects.filter(group_types__has_key=self.kwargs['group_type'])
        else:
            query = CiderGroups.objects.all()
        for group in query:
            if type(group.info_resourceids) is not list or group.info_resourceids is None:
                continue                                # Ignore group with no resources
            group_active_resources = [grid for grid in group.info_resourceids if grid in active_resources]
            if not group_active_resources:
                continue                                # Ignore group with no active resources
            og = {                                      # Extra group information to pass and use in the serializer
                'rollup_feature_ids': [],               # Feature id rollup for active resources in a group
                'rollup_org_ids': [],                   # Organization id rollup for active resources in a group
                'rollup_active_info_resourceids': group_active_resources
            }
            for grid in group_active_resources:
                active_resources[grid]['counter'] += 1                                  # A reference resource
                og['rollup_feature_ids'].extend(active_resources[grid]['feature_ids'])
                og['rollup_org_ids'].extend(active_resources[grid]['org_ids'])
            og['rollup_feature_ids'] = list(set(chain(og['rollup_feature_ids'])))       # Make unique
            og['rollup_org_ids'] = list(set(chain(og['rollup_org_ids'])))               # Make unique
            groups_extra[group.info_groupid] = og
            groups.append(group)

        for ares in active_resources.values():
            if ares['counter'] == 0:                                                    # Not a referenced resource
                continue
            rorgs = ares.get('org_ids')
            if rorgs:
                for oid in rorgs:
                    active_orgs[oid]['counter'] += 1                                    # Increment org referenced
            rfeatures = ares.get('feature_ids')
            if rfeatures:
                for fid in rfeatures:
                    all_features[fid]['counter'] += 1                                   # Increment feature referenced
                    fcid = all_features[fid].get('feature_category_id')                 # Lookup the feature category id
                    if not fcid:
                        continue
                    if fcid not in all_feature_categories:
                        continue
                    all_feature_categories[fcid]['counter'] += 1                        # Increment feature category used

        serializer = CiderACCESSActiveGroups_v1_List_Serializer(groups, context={'request': request, 'groups_extra': groups_extra}, many=True)

        active_resource_data = [ {'info_resourceid': resource.info_resourceid,
                                'cider_type': resource.cider_type,
                                'resource_descriptive_name': resource.resource_descriptive_name }
            for resource in resources if active_resources[resource.info_resourceid]['counter'] > 0 ]

        active_oids = [ org['organization_id'] for org in active_orgs.values() if org['counter'] > 0 ]
        active_org_data = [ org.other_attributes
            for org in CiderOrganizations.objects.filter(organization_id__in=active_oids) ]
        
        active_category_data = [ { 'feature_category_id': f['feature_category_id'],
                                'feature_category_name': f['feature_category_name'],
                                'feature_category_description': f['feature_category_description']}
              for f in all_feature_categories.values() if f['counter'] > 0]
              
        active_feature_data = [ {   'feature_id': f['id'],
                                'feature_name': f['name'],
                                'feature_category_id': f['feature_category_id']}
              for f in all_features.values() if f['counter'] > 0]
        
        return MyAPIResponse({'results': {
                'active_groups': serializer.data,
                'resources': active_resource_data,
                'feature_categories': active_category_data,
                'features': active_feature_data,
                'organizations': active_org_data
            }}
        )

