from django.db.models import Count
from django.conf import settings as django_settings
from django.core.paginator import Paginator
from opensearchpy import RequestError
from opensearchpy.helpers.query import Q
from opensearchpy.helpers.aggs import A
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import uri_to_iri
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .serializers import *
from cider.models import *
from glue2.models import *
from django.conf import settings
from resource_v4.process import GlobusProcess
from warehouse_tools.exceptions import MyAPIException
from warehouse_tools.responses import MyAPIResponse, CustomPagePagination
import globus_sdk

import datetime
from datetime import datetime, timedelta
import pytz
Central = pytz.timezone("US/Central")
UTC = pytz.timezone("UTC")
import logging
logg2 = logging.getLogger('warehouse.logger')

class Catalog_Search(ListAPIView):
    '''
        Catalog search and list
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)
    serializer_class = Catalog_List_Serializer
    @extend_schema(parameters=[
            OpenApiParameter('affiliations', str, OpenApiParameter.QUERY)
        ])
    def get(self, request, format=None, **kwargs):
        arg_affiliations = request.query_params.get('affiliations')
        if arg_affiliations and arg_affiliations not in ['_all_', '*']:
            want_affiliations = set(arg_affiliations.split(','))
        else:
            want_affiliations = set()

        try:
            if want_affiliations:
                final_objects = ResourceV4Catalog.objects.filter(Affiliation__in=want_affiliations)
            else:
                final_objects = ResourceV4Catalog.objects.all()
        except Exception as exc:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='{}: {}'.format(type(exc).__name__, exc))

        context={'request': request}
        serializer = Catalog_List_Serializer(final_objects, context=context, many=True)
        response_obj = {'results': serializer.data}
        return MyAPIResponse(response_obj, template_name='resource_v4/catalog_list.html')

class Catalog_Detail(GenericAPIView):
    '''
        Single Catalog retrieve by Global ID
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)
    serializer_class = Catalog_Detail_Serializer
    def get(self, request, format=None, **kwargs):
        arg_id = kwargs.get('id')
        if not arg_id:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Missing Global ID argument')

        try:
            final_objects = [ResourceV4Catalog.objects.get(pk=arg_id)]
        except ResourceV4Catalog.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified Global ID not found')

        context = {}
        serializer = Catalog_Detail_Serializer(final_objects, context=context, many=True)
        response_obj = {'results': serializer.data}
        return MyAPIResponse(response_obj, template_name='resource_v4/catalog_detail.html')

#
# Local Views
#
class Local_Search(ListAPIView):
    '''
        Local resource search and list
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)
    serializer_class = Local_List_Serializer
    @extend_schema(parameters=[
            OpenApiParameter('affiliations', str, OpenApiParameter.QUERY),
            OpenApiParameter('localids', str, OpenApiParameter.QUERY),
            OpenApiParameter('localtypes', str, OpenApiParameter.QUERY),
            OpenApiParameter('page', int, OpenApiParameter.QUERY),
            OpenApiParameter('page_size', int, OpenApiParameter.QUERY)
        ])
    def get(self, request, format=None, **kwargs):
        arg_affiliations = request.query_params.get('affiliations')
        if not arg_affiliations:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Required affiliation not specified')

        arg_localids = request.query_params.get('localids')
        if arg_localids:
            want_localids = set(arg_localids.split(','))
        else:
            want_localids = set()

        arg_localtypes = request.query_params.get('localtypes')
        if arg_localtypes:
            want_localtypes = set(arg_localtypes.split(','))
        else:
            want_localtypes = set()

        raw_page = request.query_params.get('page')
        if raw_page:
            try:
                page = int(raw_page)
                if page == 0: raise
            except:
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified page "{}" not valid'.format(raw_page))
        else:
            page = None
        try:
            raw_page_size = request.query_params.get('page_size', 25)
            page_size = int(raw_page_size)
        except:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified page_size "{}" not valid'.format(raw_page_size))

        response_obj = {}

        try:
            objects = ResourceV4Local.objects.filter(Affiliation__exact=arg_affiliations)
            if want_localids:
                objects = objects.filter(LocalID__in=want_localids)
            if want_localtypes:
                objects = objects.filter(LocalType__in=want_localtypes)

            if page:
                paginator = Paginator(objects, page_size)
                final_objects = paginator.page(page)
                response_obj['page'] = page
                response_obj['total_pages'] = paginator.num_pages
            else:
                final_objects = objects
        except Exception as exc:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='{}: {}'.format(type(exc).__name__, exc))

        context={'request': request}
        serializer = Local_List_Serializer(final_objects, context=context, many=True)
        response_obj['results'] = serializer.data
        return MyAPIResponse(response_obj, template_name='resource_v4/local_list.html')

class Local_Detail(GenericAPIView):
    '''
        Single Local resource retrieve by Global ID
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)
    serializer_class = Local_Detail_Serializer
    def get(self, request, format=None, **kwargs):
        arg_id = kwargs.get('id')
        if not arg_id:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Missing Global ID argument')

        try:
            final_objects = [ResourceV4Local.objects.get(pk=arg_id)]
        except ResourceV4Local.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified Global ID not found')

        context = {}
        serializer = Local_Detail_Serializer(final_objects, context=context, many=True)
        response_obj = {'results': serializer.data}
        return MyAPIResponse(response_obj, template_name='resource_v4/local_detail.html')

#
# List Resource Groups, Types, and counts in each combination
#
class Resource_Types_List(ListAPIView):
    '''
        Resource Group and Types search and list
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)
    serializer_class = Resource_Types_Serializer
    @extend_schema(parameters=[
            OpenApiParameter('affiliations', str, OpenApiParameter.QUERY),
            OpenApiParameter('page', int, OpenApiParameter.QUERY),
            OpenApiParameter('page_size', int, OpenApiParameter.QUERY)
        ])
    def get(self, request, format=None, **kwargs):
        arg_affiliations = request.query_params.get('affiliations')
        if arg_affiliations and arg_affiliations not in ['_all_', '*']:
            want_affiliations = set(arg_affiliations.split(','))
        else:
            want_affiliations = set()

        response_obj = {}

        try:
            if want_affiliations:
                objects = ResourceV4.objects.filter(Affiliation__in=want_affiliations).\
                    values('ResourceGroup','Type').annotate(count=Count(['ResourceGroup','Type']))
            else:
                objects = ResourceV4.objects.all().\
                    values('ResourceGroup','Type').annotate(count=Count(['ResourceGroup','Type']))
            objects = objects.order_by('ResourceGroup', 'Type')
            response_obj['total_results'] = len(objects)
            final_objects = objects
        except Exception as exc:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='{}: {}'.format(type(exc).__name__, exc))
        context = {}
        serializer = Resource_Types_Serializer(final_objects, context=context, many=True)
        response_obj['results'] = serializer.data
        return MyAPIResponse(response_obj, template_name='resource_v4/types_list.html')

#
# Resource Views and supporting functions
#
def resource_topics_filter(input_objects, search_topics_set):
    # Inspect objects because we can't push this filter to the database
    filtered_objects = []
    for obj in input_objects:
        objtopics = obj.Topics
        if len(objtopics or '') < 1: # Skip objects without a topics
            continue
        objtopics_list = set(objtopics.split(','))
        if not objtopics_list.isdisjoint(search_topics_set):
            filtered_objects.append(obj)
    return(filtered_objects)

def resource_subtotals(input_objects):
    affiliation_totals = {}
    topic_totals    = {}
    type_totals     = {}
    provider_totals = {}
    for obj in input_objects:
        this_affiliation = obj.Affiliation
        affiliation_totals[this_affiliation] = affiliation_totals.get(this_affiliation, 0) + 1
        this_topics = obj.Topics
        if this_topics:
            for x in this_topics.split(','):
                topics_totals[x] = topics_totals.get(x, 0) + 1
        this_provider = obj.ProviderID
        if this_provider:
            provider_totals[this_provider] = provider_totals.get(this_provider, 0) + 1
        this_type = obj.ResourceGroup + ':' + obj.Type
        type_totals[this_type] = type_totals.get(this_type, 0) + 1
    affiliation_return = [ {'Affiliation': key, 'subtotal': value} for key, value in affiliation_totals.items() ]
    topics_return = [ {'id': key, 'subtotal': value} for key, value in topics_totals.items() ]
    provider_return = [ {'ProviderID': key, 'subtotal': value} for key, value in provider_totals.items() ]
    type_return = [ {'id': key, 'subtotal': value} for key, value in type_totals.items() ]
    return({'affiliations': affiliation_return, 'topics': topics_return,
           'types': type_return, 'providers': provider_return})

def resource_terms_filtersort(input_objects, search_terms_set, sort_field='name'):
    # This function inspects and sorts objects using an algorithm that is too complex to do using SQL
    # Sorting algorithms requirements:
    #   First prioritize resources with a tag/keyword matching at least one search term
    #     Example: given search terms "frog spectrometer chuckles", resources with a "spectrometer" tag should
    #     be listed before resources with no tags matching a search term
    #   Second, prioritize resources with resource_name and resource_description matching ALL of the search terms.
    #     Example: gieven search terms "frog spectrometer chuckles", resources with ALL those words in
    #     resource_description and/or resource_name should be listed before resources with some matching terms.
    #   Third, prioritize resources with resource_name and resource_description matching SOME of the search terms.
    #     In this case, ordering sould be based on the total number of occurances of the search terms.
    #     For example, if the search term is "python", resources that have the term three times should be listed
    #     before resources with that term happening 2 times or once.
    #
    # SORT_KEY fields:
    #   <B_RANK>:<C_RANK>:<D_RANK>:<D_RANK>:<SORT_SUFFIX>
    # Where:
    #   A_RANK: all terms matched Name; RANK=999 minus how many keywords matched
    #   B_RANK: keyword match; RANK=999 minus how many keywords matched
    #   C_RANK: all terms matched Name, Short Description, or Description; RANK=999 minus how many terms matched
    #   D_RANK: some terms matched Name, Short Description, or Description; RANK=999 minus total number of words matching terms
    # Where "999 minus match count" makes higher match counts sort firts alphabetically (996=999-3 before 998=999-1)
    sort_array = {}
    
    for obj in input_objects:
        name_words_set = set(obj.Name.replace(',', ' ').lower().split())
        name_rank = len(name_words_set.intersection(search_terms_set))                  # How many matches
        if name_rank == len(search_terms_set):                                          # All terms matched Name
            A_RANK = u'{:03d}'.format(999-name_rank)
        else:
            A_RANK = u'999'
        
        keyword_set = set((obj.Keywords or '').replace(',', ' ').lower().split())       # Empty string '' if Null
        keyword_rank = len(keyword_set.intersection(search_terms_set))                  # How many keyword matches
        B_RANK = u'{:03d}'.format(999-keyword_rank)

        name_desc_words = u' '.join((obj.Name, (obj.ShortDescription or ''), (obj.Description or ''))).replace(',', ' ').lower().split()
        name_desc_rank = len(set(name_desc_words).intersection(search_terms_set))       # How many matches
        if name_desc_rank == len(search_terms_set):                                     # All terms matched Name, Short Description or Description
            C_RANK = u'{:03d}'.format(999-name_desc_rank)
        else:
            C_RANK = u'999'
                
        total_matches = [word in search_terms_set for word in name_desc_words].count(True)  # How many times terms appear
        D_RANK = u'{:03d}'.format(999-total_matches)

        all_RANKS = u':'.join((A_RANK, B_RANK, C_RANK, D_RANK))
        if all_RANKS == u'999:999:999:999':                                             # No matches
            continue                                                                    # Loop to discard this object

        if sort_field == 'StartDateTime':
            SORT_SUFFIX = obj.StartDateTime.astimezone(UTC).strftime('%Y-%m-%dT%H:%M:%S%z')
        else: # sort_field == 'name':
            SORT_SUFFIX = (obj.Name or '').lower()

        SORT_KEY = u':'.join((all_RANKS, SORT_SUFFIX, str(obj.ID)))
        sort_array[SORT_KEY] = obj

    filtered_objects = [sort_array[key] for key in sorted(sort_array.keys())]
    return(filtered_objects)

def resource_strings_filtersort(input_objects, search_strings_set, sort_field='name'):
    # This function inspects and sorts objects using an algorithm that is too complex to do using SQL
    # Sorting algorithms requirements:
    #   First prioritize resources with a tag/keyword matching at least one search string
    #     Example: given search strings "spec soft", resources with a "software" tag should
    #     be listed before resources with no tags matching a search string
    #   Second, prioritize resources with resource_name and resource_description matching ALL of the search strings.
    #     Example: gieven search terms "spec soft", resources with ALL those strings in
    #     resource_description and/or resource_name should be listed before resources matching one strings.
    #   Third, prioritize resources with resource_name and resource_description matching SOME of the search strings.
    #     In this case, ordering sould be based on the total number of occurances of the search strings.
    #     For example, if the search strings is "soft", resources that have the term three times should be listed
    #     before resources with that string happening 2 times or once.

    # SORT_KEY fields:
    #   <B_RANK>:<C_RANK>:<D_RANK>:<D_RANK>:<SORT_SUFFIX>
    # Where:
    #   A_RANK: all strings matched Name; RANK=999 minus how many strings matched
    #   B_RANK: keyword match; RANK=999 minus how many keywords matched
    #   C_RANK: all strings matched Name or Description; RANK=999 minus how many strings matched
    #   D_RANK: some strings matched Name or Description; RANK=999 minus total number of words matching strings
    # Where "999 minus match count" makes higher match counts sort firts alphabetically (996=999-3 before 998=999-1)
    sort_array = {}
    search_for_set = set([x.lower() for x in search_strings_set])
    
    for obj in input_objects:
        search_in = obj.Name.lower()
        name_rank = [search_for in search_in for search_for in search_for_set].count(True)
        if name_rank != len(search_for_set):                                         # All terms matched Name
            name_rank = 0
        A_RANK = u'{:03d}'.format(999-name_rank)
    
        search_in_set = set((obj.Keywords or '').replace(',', ' ').lower().split())  # Empty string '' if Null
        keyword_rank = 0
        for search_in in search_in_set:
            if [search_for in search_in for search_for in search_for_set].count(True) > 0:
                keyword_rank += 1
        B_RANK = u'{:03d}'.format(999-keyword_rank)

        search_in = u' '.join((obj.Name, (obj.ShortDescription or ''), obj.Description)).replace(',', ' ').lower()
        name_desc_rank = [search_for in search_in for search_for in search_for_set].count(True)
        if name_desc_rank != len(search_for_set):                                    # All terms matched Name, Short Description, or Description
            name_desc_rank = 0
        C_RANK = u'{:03d}'.format(999-name_desc_rank)

        total_matches = 0
        for search_for in search_for_set:
            total_matches += search_in.count(search_for)
        D_RANK = u'{:03d}'.format(999-total_matches)

        all_RANKS = u':'.join((A_RANK, B_RANK, C_RANK, D_RANK))
        if all_RANKS == u'999:999:999:999':                                          # No matches
            continue                                                                 # Loop to discard this object

        if sort_field == 'StartDateTime':
            SORT_SUFFIX = obj.StartDateTime.strftime('%Y-%m-%dT%H:%M:%S%z')
        else: # sort_field == 'name':
            SORT_SUFFIX = (obj.Name or '').lower()

        SORT_KEY = u':'.join((all_RANKS, SORT_SUFFIX, str(obj.ID)))
        sort_array[SORT_KEY] = obj

    filtered_objects = [sort_array[key] for key in sorted(sort_array.keys())]
    return(filtered_objects)

class Resource_Detail(GenericAPIView):
    '''
        Single Resource retrieve by Global ID or by Affiliation and Local ID
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)
    serializer_class = Resource_Detail_Serializer
    def get(self, request, format=None, **kwargs):
        arg_id = kwargs.get('id')
        if not arg_id:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Missing Global ID argument')
            
        try:
            final_objects = [ResourceV4.objects.get(pk=arg_id)]
        except ResourceV4.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified Global ID not found')

        context = {'request': request}
        serializer = Resource_Detail_Serializer(final_objects, context=context, many=True)
        response_obj = {'results': serializer.data}
            
        return MyAPIResponse(response_obj, template_name='resource_v4/resource_detail.html')

class Resource_Search(ListAPIView):
    '''
        Resource search and list
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)
    serializer_class = Resource_Search_Serializer
    @extend_schema(parameters=[
            OpenApiParameter('search_terms', str, OpenApiParameter.QUERY),
            OpenApiParameter('search_strings', str, OpenApiParameter.QUERY),
            OpenApiParameter('affiliations', str, OpenApiParameter.QUERY),
            OpenApiParameter('resource_groups', str, OpenApiParameter.QUERY),
            OpenApiParameter('types', str, OpenApiParameter.QUERY),
            OpenApiParameter('qualitylevels', str, OpenApiParameter.QUERY),
            OpenApiParameter('topics', str, OpenApiParameter.QUERY),
            OpenApiParameter('providers', str, OpenApiParameter.QUERY),
            OpenApiParameter('sort', str, OpenApiParameter.QUERY),
            OpenApiParameter('subtotals', str, OpenApiParameter.QUERY),
            OpenApiParameter('page', int, OpenApiParameter.QUERY),
            OpenApiParameter('page_size', int, OpenApiParameter.QUERY)
        ])
    def get(self, request, format=None, **kwargs):
        # Process optional arguments
        arg_affiliations = request.query_params.get('affiliations')
        if arg_affiliations and arg_affiliations not in ['_all_', '*']:
            want_affiliations = set(arg_affiliations.split(','))
        else:
            want_affiliations = set()

        arg_resource_groups = request.query_params.get('resource_groups')
        want_resource_groups = list()
        if arg_resource_groups:
            # We normalize case if lower of what was entered is in our map, otherwise we leave what was entered
            rg_map = { item.lower(): item for item in
                ['Computing Tools and Services', 'Data Resources', 'Guides', 'Live Events', 'Organizations', 'Software', 'Streamed Events'] }
            for item in arg_resource_groups.split(','):
                want_resource_groups.append(rg_map.get(item.lower(), item))

        arg_types = request.query_params.get('types')
        if arg_types:
            want_types = set(arg_types.split(','))
        else:
            want_types = set()

        arg_qualitylevels = request.query_params.get('qualitylevels', kwargs.get('qualitylevels', 'production'))
        want_qualitylevels = list()
        if arg_qualitylevels and arg_qualitylevels not in ['_all_', '*']:
            # We normalize case if the lower of what was entered is in our map, otherwise we leave the case
            quality_map = { item.lower(): item for item in
                    ['Decommissioned', 'Preliminary', 'Pre-production', 'Production', 'Testing', 'Unsupported'] }
            for item in arg_qualitylevels.split(','):
                want_qualitylevels.append(quality_map.get(item.lower(), item))

        arg_terms = request.query_params.get('search_terms')
        if arg_terms:
            want_terms = set(arg_terms.replace(',', ' ').lower().split())
        else:
            want_terms = set()

        arg_strings = request.query_params.get('search_strings')
        if arg_strings:
            want_strings = set(arg_strings.replace(',', ' ').lower().split())
        else:
            want_strings = set()

        arg_topics = request.query_params.get('topics')
        if arg_topics:
            want_topics = set(arg_topics.split(','))
        else:
            want_topics = set()

        arg_providers = request.query_params.get('providers')
        # Search in ProviderID field if possible rather than Provider in JSONField
        if arg_providers:
            if set(arg_providers).issubset(set('0123456789,')):
                # Handle numeric providers for uiuc.edu
                if want_affiliations and len(want_affiliations) == 1:
                    this_affiliation = next(iter(want_affiliations))
                    want_providerids = ['urn:glue2:GlobalResourceProvider:{}.{}'.format(x.strip(), this_affiliation) for x in arg_providers.split(',')]
                    want_providers = []
                else:
                    want_providerids = []
                    want_providers = [int(x) for x in arg_providers.split(',') if x.strip().isdigit()]
            else:
                want_providerids = set(arg_providers.split(','))
                want_providers = []
        else:
            want_providerids = []
            want_providers = []

        sort = request.query_params.get('sort', 'Name')

        raw_page = request.query_params.get('page')
        if raw_page:
            try:
                page = int(raw_page)
                if page == 0: raise
            except:
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified page "{}" not valid'.format(raw_page))
        else:
            page = None
        try:
            raw_page_size = request.query_params.get('page_size', 25)
            page_size = int(raw_page_size)
        except:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified page_size "{}" not valid'.format(raw_page_size))

        arg_subtotals = request.query_params.get('subtotals', None)
        if arg_subtotals:
            arg_subtotals = arg_subtotals.lower()

        response_obj = {}
        try:
            # These filters are handled by the database; they are first
            objects = ResourceV4.objects.filter(QualityLevel__exact='Production')
            if want_affiliations:
                objects = objects.filter(Affiliation__in=want_affiliations)
            if want_resource_groups:
                objects = objects.filter(ResourceGroup__in=want_resource_groups)
            if want_types:
                objects = objects.filter(Type__in=want_types)
            if want_providerids:
                objects = objects.filter(ProviderID__in=want_providerids)
#            elif want_providers:
#                objects = objects.filter(EntityJSON__provider__in=want_providers)
            if not want_terms and sort is not None: # Becase terms search does its own ranked sort
                objects = objects.order_by(sort)

            # These filters have to be handled with code; they must be after the previous database filters
            if want_topics:
                objects = resource_topics_filter(objects, want_topics)
            if want_terms:
                objects = resource_terms_filtersort(objects, want_terms, sort_field='name')
            elif want_strings:
                objects = resource_strings_filtersort(objects, want_strings, sort_field='name')

            response_obj['total_results'] = len(objects)
            if arg_subtotals in ('only', 'include'):
                response_obj['subtotals'] = resource_subtotals(objects)
                if arg_subtotals == 'only':
                    return MyAPIResponse(response_obj, template_name='resource_v4/resource_list.html')

            if page:
                paginator = Paginator(objects, page_size)
                final_objects = paginator.page(page)
                response_obj['page'] = page
                response_obj['total_pages'] = paginator.num_pages
            else:
                final_objects = objects
        except Exception as exc:
            logg2.info(exc, exc_info=True)
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='{}: {}'.format(type(exc).__name__, exc))

        context = {'request': request}
        serializer = Resource_Search_Serializer(final_objects, context=context, many=True)
        response_obj['results'] = serializer.data
        return MyAPIResponse(response_obj, template_name='resource_v4/resource_list.html')
        
class Resource_ESearch(ListAPIView):
    '''
        Resource ElasticSearch/OpenSearch and list

        Results are ordered by relevance (_score)
        
        Optional selection argument(s):
        ```
            search_terms=<comma_delimited_search_terms>
            search_fields=<any-combination-of: Name,Topics,Keywords,ShortDescription,Description
            affiliations=<comma-delimited-list>
            resource_groups=<comma-delimited-list>
            types=<comma-delimited-list>
            qualitylevels=*|<level1>[,<level2>[...]]            (default=production)
            topics=<comma-delimited-list>
            keywords=<comma-delimited-list>
            providers=<comma-delimited-providerid-list>
            idprefix=<an-id-prefix>
            relation=[!]<relatedid>
            aggregations=[affiliation|resourcegroup|type|qualitylevel|providerid]
        ```
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)
    serializer_class = Resource_ESearch_Serializer
    @extend_schema(parameters=[
            OpenApiParameter('search_terms', str, OpenApiParameter.QUERY),
            OpenApiParameter('search_strings', str, OpenApiParameter.QUERY),
            OpenApiParameter('affiliations', str, OpenApiParameter.QUERY),
            OpenApiParameter('resource_groups', str, OpenApiParameter.QUERY),
            OpenApiParameter('types', str, OpenApiParameter.QUERY),
            OpenApiParameter('qualitylevels', str, OpenApiParameter.QUERY),
            OpenApiParameter('topics', str, OpenApiParameter.QUERY),
            OpenApiParameter('keywords', str, OpenApiParameter.QUERY),
            OpenApiParameter('providers', str, OpenApiParameter.QUERY),
            OpenApiParameter('idprefix', str, OpenApiParameter.QUERY),
            OpenApiParameter('relation', str, OpenApiParameter.QUERY),
            OpenApiParameter('aggregations', str, OpenApiParameter.QUERY),
            OpenApiParameter('page', int, OpenApiParameter.QUERY),
            OpenApiParameter('page_size', int, OpenApiParameter.QUERY)
        ])
    def get(self, request, format=None, **kwargs):
        if not django_settings.OSCON:
            raise MyAPIException(code=status.HTTP_503_SERVICE_UNAVAILABLE, detail='OpenSearch not available')
        
        ### Process optional arguments
        arg_affiliations = request.query_params.get('affiliations')
        if arg_affiliations and arg_affiliations not in ['_all_', '*']:
            want_affiliations = list(arg_affiliations.split(','))
        else: # No selected affiliations means all affiliations
            want_affiliations = list()

        arg_resource_groups = request.query_params.get('resource_groups')
        want_resource_groups = list()
        if arg_resource_groups:
            # We normalize case if lower of what was entered is in our map, otherwise we leave what was entered
            rg_map = { item.lower(): item for item in
                ['Computing Tools and Services', 'Data Resources', 'Guides', 'Live Events', 'Organizations', 'Software', 'Streamed Events'] }
            for item in arg_resource_groups.split(','):
                want_resource_groups.append(rg_map.get(item.lower(), item))

        arg_types = request.query_params.get('types')
        if arg_types:
            want_types = list(arg_types.split(','))
        else:
            want_types = list()

        arg_qualitylevels = request.query_params.get('qualitylevels', 'production')
        want_qualitylevels = list()
        if arg_qualitylevels and arg_qualitylevels not in ['_all_', '*']:
            # We normalize case if lower of what was entered is in our map, otherwise we leave what was entered
            quality_map = { item.lower(): item for item in
                    ['Decommissioned', 'Preliminary', 'Pre-production', 'Production', 'Testing', 'Unsupported'] }
            for item in arg_qualitylevels.split(','):
                want_qualitylevels.append(quality_map.get(item.lower(), item))

        arg_terms = request.query_params.get('search_terms', None)
        want_terms = list()
        want_wildcard_terms = list()
        if arg_terms:
            for term in arg_terms.replace(',', ' ').lower().split():
                if '*' in term:
                    want_wildcard_terms.append(term)
                else:
                    want_terms.append(term)
        if len(want_wildcard_terms) > 1:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Only one wildcard term allowed')

        # Search any valid subset of fields_all passed in search_fields
        arg_fields = request.query_params.get('search_fields', None)
        fields_all = ['Name', 'Topics', 'Keywords', 'ShortDescription', 'Description']
        fields_map = { item.lower(): item for item in fields_all }
        want_fields = list()
        if arg_fields and arg_fields.lower() not in ['_all_', '*']:
            for item in arg_fields.replace(',', ' ').lower().split():
                want_fields.append(fields_map.get(item, item)) # The lookup value, or the value itself
        if not want_fields:     # Default is to search all fields
            want_fields = fields_all

        arg_topics = request.query_params.get('topics', None)
        if arg_topics:
            want_topics = list(arg_topics.split(','))
        else:
            want_topics = list()

        arg_keywords = request.query_params.get('keywords', None)
        if arg_keywords:
            want_keywords = list(arg_keywords.split(','))
        else:
            want_keywords = list()

        arg_providers = request.query_params.get('providers', None)
        # Search in ProviderID field if possible rather than Provider in JSONField
        if arg_providers:
            want_providerids = list(arg_providers.split(','))
        else:
            want_providerids = list()

        arg_idprefix = request.query_params.get('idprefix', None)
        # Search for ID fields that start with this prefix
        if arg_idprefix:
            if arg_idprefix[-1] in ('%', '*'):
                want_idprefix = arg_idprefix[:-1]
            else:
                want_idprefix = arg_idprefix
        else:
            want_idprefix = False

        arg_relation = request.query_params.get('relation', None)
        if arg_relation:
            want_relationinvert = (arg_relation[0] == '!')
            if want_relationinvert:
                arg_relation = arg_relation[1:]
            want_relationid = arg_relation
        else:
            want_relationid = False

        arg_aggregations = request.query_params.get('aggregations', None)
        # Return OpenSearch aggregations
        if arg_aggregations:
            want_aggregations = list(x.lower() for x in arg_aggregations.split(','))
        else:
            want_aggregations = list()

        raw_page = request.query_params.get('page')
        if raw_page:
            try:
                page = int(raw_page)
                if page == 0: raise
            except:
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified page "{}" not valid'.format(raw_page))
        else:
            page = None
        try:
            raw_page_size = request.query_params.get('page_size', 25)
            page_size = int(raw_page_size)
        except:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Specified page_size "{}" not valid'.format(raw_page_size))

        extra_response = {}      # Extras to return in the response

        # Build the query, starting with result filters, and then queries that rank results
        try:
            ES = ResourceV4Index.search(using=django_settings.OSCON)

            # These FILTERs control which rows the index returns
            if want_affiliations:
                ES = ES.filter('terms', Affiliation=want_affiliations)
            if want_resource_groups:
                ES = ES.filter('terms', ResourceGroup=want_resource_groups)
            if want_types:
                ES = ES.filter('terms', Type=want_types)
            if want_qualitylevels:
                ES = ES.filter('terms', QualityLevel=want_qualitylevels)
            if want_providerids:
                ES = ES.filter('terms', ProviderID=want_providerids)
            if want_idprefix:
                ES = ES.filter('prefix', ID=want_idprefix)
            if want_relationid:
                if want_relationinvert:
                    ES = ES.filter(
                        'bool', must_not=
                        Q('nested', path='Relations', query=
                            Q('bool', filter=
                            Q('term', Relations__RelatedID__keyword=want_relationid)))
                        )
                else:
                    ES = ES.filter(
                        'bool', must=
                        Q('nested', path='Relations', query=
                            Q('bool', filter=
                            Q('term', Relations__RelatedID__keyword=want_relationid)))
                        )

            # The QUERYs that control how rows are ranked
            if want_topics:
                ES = ES.query('match', Topics=arg_topics)
            if want_keywords:
                ES = ES.query('match', Keywords=arg_keywords)
            if want_terms:
                ES = ES.query('multi_match', query=' '.join(want_terms), fields=want_fields)
            if want_wildcard_terms:
                SUBQ = []
                for field in want_fields:
                    SUBQ.append(Q({'wildcard': {field: want_wildcard_terms[0]}}))
                ES = ES.query('bool', should=SUBQ)

            # If the user didn't enter search terms use a default non-filtering query that does not
            #   exclude non-matches but produces results ordered by the default query matching score
            USER_QUERIES = want_topics or want_keywords or want_terms or want_wildcard_terms
            if not USER_QUERIES:
                # Default ordering for 'Cloud Image' where the 'featured' keyword is used
                if len(want_types) == 1 and want_types[0] == 'Cloud Image':
                    ES = ES.query('bool', minimum_should_match=-1, should=
                        Q('match', Keywords='featured' ))
                # Everything else doesn't have a default query or ordering so we inject 'featured'
                else: # 'featured' may not be known to be used, but is useful
                    ES = ES.query('bool', minimum_should_match=-1, should=
                        Q('match', Keywords='featured' ))

            # Request aggregations
            if want_aggregations:
                field_map = { item.lower(): item for item in
                    ['Affiliation', 'ResourceGroup', 'Type', 'QualityLevel', 'ProviderID'] }
                for field in want_aggregations:
                    if field in field_map:
                        realfield = field_map[field]
                        ES.aggs.bucket(realfield, A('terms', field=realfield))

            ES = ES.extra(from_ = 0, size = 1000)       # Limit to 1000 results
#            ES = ES.extra(explain=True)
            es_results = ES.execute()
 
            if page:
                paginator = CustomPagePagination()
                results_page = paginator.paginate_queryset(es_results.hits.hits, request, view=self)
            else:
                results_page = es_results.hits.hits

            results_dicts = []
            for row in results_page:
                row_dict = row['_source'].to_dict()
                row_dict['_score'] = row['_score']
                try:
                    for rel in row_dict['Relations']:
                        rel['ID'] = rel.pop('RelatedID')
                        related = ResourceV4Index.Lookup_Relation(rel['ID'])
                        if related:
                            rel['Name'] = related.get('Name')
                        try:
                            rel['DetailURL'] = request.build_absolute_uri(uri_to_iri(reverse('resource-detail', args=[rel['ID']])))
                        except:
                            pass
                except:
                    pass
                try:
                    row_dict['DetailURL'] = request.build_absolute_uri(uri_to_iri(reverse('resource-detail', args=[row_dict['ID']])))
                except:
                    pass
                results_dicts.append(row_dict)

            aggregations = {}
            if 'aggregations' in es_results:
                for aggkey in dir(es_results.aggregations):
                    buckets = []
                    for item in es_results.aggregations[aggkey].buckets:
                        itemdict = item.to_dict()
                        bucket = { 'count': itemdict['doc_count'] }
                        if aggkey != 'ProviderID':
                            bucket['Name'] = itemdict['key']
                        else: # For ProviderIDs lookup the cached Name
                            bucket['ID'] = itemdict['key']
                            provider = ResourceV4Index.Lookup_Relation(itemdict['key'])
                            if provider:
                                bucket['Name'] = provider.get('Name', itemdict['key'])
                            else:
                                bucket['Name'] = itemdict['key']
                        buckets.append(bucket)
                    aggregations[aggkey] = buckets
            if aggregations:
                extra_response['aggregations'] = aggregations

        except RequestError as exc:
            if exc.error == 'search_phase_execution_exception':
                try:
                    reason = exc.info['error']['root_cause'][0]['reason']
                    if not reason.startswith('Result window is too large'): pass
                finally:
                    logg2.warning(exc)
                    raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Unable to page that far into results, narrow your search') from None
            logg2.info(exc, exc_info=True)
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='{}: {}'.format(type(exc).__name__, exc))

        except Exception as exc:
            logg2.info(exc, exc_info=True)
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='{}: {}'.format(type(exc).__name__, exc))

        try:
            extra_response['count'] = ES.count()
        except:
            pass
            
        if page:
            return paginator.get_paginated_response(results_dicts, request, **extra_response)
        else:
            return MyAPIResponse({'results': results_dicts, **extra_response}, template_name='resource_v4/resource_list.html')

##
## Cache Management Views
##
class Relations_Cache(GenericAPIView):
    '''
        Load Relations Cache
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)
    serializer_class = Relations_Cache_Serializer
    def get(self, request, format='json', **kwargs):
        start_utc = datetime.now(timezone.utc)
        count = ResourceV4Index.Cache_Lookup_Relations()
        response_obj = {'cached': count, 'seconds': (datetime.now(timezone.utc) - start_utc).total_seconds()}
        return MyAPIResponse(response_obj)


class SearchGlobus(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = None

    def __init__(self, *args, **kwargs):
        self.allowed_params = ['q', 'filter', 'fields', 'sort_by', 'limit', 'offset']
        self.app = globus_sdk.ClientApp(
            "ACCESS-CI Operations Warehouse Globus Service Client",
            client_id=settings.GLOBUS_CLIENT_ID,
            client_secret=settings.GLOBUS_CLIENT_SECRET
        )
        self.search_client = globus_sdk.SearchClient(app=self.app)
        self.search_endpoint = settings.GLOBUS_SEARCH_INDEX_ID
        super().__init__(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Perform a quick query on the Globus search endpoint
        cleaned_params = {}
        if "q" not in request.query_params.lists():
            cleaned_params["q"] = "*"

        for query_param in request.query_params.lists():
            if query_param[0] not in self.allowed_params:
                return Response(
                    {"error": f"Invalid query parameter: {query_param[0]}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cleaned_params[query_param[0]] = request.query_params[query_param[0]]

        search_query = globus_sdk.SearchQueryV1(**cleaned_params)
        search = self.search_client.post_search(
            self.search_endpoint,
            search_query
        )
        return Response(search)


@api_view(["GET"])
def compare_warehouse_view(request, *args, **kwargs):

    # Simulate incoming content items from GLUE2 router
    glue2_remote_resources = ApplicationHandle.objects.order_by(
        "-CreationTime").select_related()

    # Build resourceV4 payload from remote GLUE2 resources (simulate incoming GLUE2 models in router)
    payload = generate_payloads(glue2_remote_resources)

    # Initiate a Globus Process
    # Handles ingest, delete_by_query, and update.
    globus_process = GlobusProcess()

    # Process added/removed/updated items in ResourceV4Local table
    if len(payload["added"]):
        # Ingest new items into Globus Search Index
        gmeta_list = {
            "ingest_type": "GMetaList",
            "ingest_data": {
                "gmeta": []
            }
        }
        for item in payload["added"]:
            gmeta_entry = {
                "subject": item["ID"],
                "visible_to": ["public"],
                "content": item["EntityJSON"]
            }
            gmeta_list["ingest_data"]["gmeta"].append(gmeta_entry)
        globus_process.ingest(gmeta_list=gmeta_list)

        # Bulk create new ResourceV4Local entries for added items in PostgreSQL
        resource_v4_local_added = [
            ResourceV4Local(**item) for item in payload["added"]
        ]
        try:
            ResourceV4Local.objects.bulk_create(resource_v4_local_added)
        except Exception as err:
            logg2.warning(err)
            return Response(
                [{"error": str(err)}],
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    if len(payload["removed"]):
        # Delete items from Globus Search Index by querying on the ID field
        globus_process.delete_by_query(payload["removed"])

        # Delete items from ResourceV4Local table in PostgreSQL
        resource_v4_local_removed = ResourceV4Local.objects.filter(
            LocalID__in=payload["removed"]
        )
        try:
            resource_v4_local_removed.delete()
        except Exception as err:
            logg2.warning(err)
            return Response(
                [{"error": str(err)}],
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    if len(payload["updated"]):
        # Ingest updated items into Globus Search Index
        gmeta_list = {
            "ingest_type": "GMetaList",
            "ingest_data": {
                "gmeta": []
            }
        }

        for item in payload["updated"]:
            try:
                resource = ResourceV4Local.objects.get(LocalID=item["LocalID"])
                for key, value in item["changes"].items():
                    if key == "EntityJSON":
                        for entity_json_key, entity_json_value in value.items():
                            resource.EntityJSON[entity_json_key] = entity_json_value
                    else:
                        setattr(resource, key, value)
                resource.save()

                gmeta_entry = {
                    "subject": resource.ID,
                    "visible_to": ["public"],
                    "content": resource.EntityJSON
                }
                gmeta_list["ingest_data"]["gmeta"].append(gmeta_entry)
            except Exception as err:
                logg2.warning(err)
                return Response(
                    [{"error": str(err)}],
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        globus_process.update_by_subject(gmeta_list=gmeta_list)

    logg2.info(payload)
    return Response([{
        "added": len(payload["added"]),
        "removed": len(payload["removed"]),
        "updated": len(payload["updated"]),
    }])


@api_view(["GET"])
def populate_resource_v4_local_view(request, *args, **kwargs):
    # Initial ingest of access-ci data into Globus
    try:
        remote_response = requests.get(
            "https://operations-api.access-ci.org/wh2/resource/v4/local_search/",
            params={
                "affiliations": "access-ci.org",
            },
            headers={
                "Content-Type": "application/json"
            }
        )
        remote_response.raise_for_status()
    except Exception as err:
        return Response(err)

    software_models = []
    for software in remote_response.json()["results"]:
        software.pop("DetailURL")
        software_models.append(ResourceV4Local(**software))
    try:
        from django.db import IntegrityError
        ResourceV4Local.objects.bulk_create(software_models)
    except IntegrityError as err:
        if "duplicate key" in str(err).lower():
            return Response(
                "Duplicate key error: Some records already exist in ResourceV4Local", 
                status=status.HTTP_409_CONFLICT
            )

    return Response(f"Inserted {len(software_models)} records into ResourceV4Local")


def generate_payloads(application_handles):
    import hashlib

    def chunk_dict(data_dict, chunk_size):
        for i in range(0, len(data_dict), chunk_size):
            yield data_dict[i:i + chunk_size]

    # Current list of resource_v4_local entries in DB
    resource_v4_local_list_new = []
    resource_v4_local_list_old = ResourceV4Local.objects.filter(
        Affiliation__exact="access-ci.org"
    ).order_by("-CreationTime")

    for chunk in chunk_dict(application_handles, 250):
        for application in chunk:
            cider = CiderInfrastructure.objects.filter(
                info_resourceid=application.ResourceID
            ).first()
            environment_id = application.ID
            environment_id_utf8 = environment_id.encode('utf-8')
            environment_id_hash = f"urn:ogf.org:glue2:access-ci.org:executable.software:{hashlib.md5(environment_id_utf8).hexdigest()}"

            validity = application.ApplicationEnvironment.Validity
            if validity:
                validity = str(validity.total_seconds())

            # Build EntityJSON for the software entity
            entity_json = {
                "ID": environment_id_hash,
                "Category": application.ApplicationEnvironment.EntityJSON.get("Category", None),
                "CreationTime": application.ApplicationEnvironment.CreationTime.isoformat(),
                "Default": application.ApplicationEnvironment.EntityJSON.get("Default", True),
                "Description": application.ApplicationEnvironment.Description,
                "HandleKey": application.Value,
                "HandleType": application.Type,
                "Keywords": application.ApplicationEnvironment.EntityJSON.get("Keywords", None),
                "LocalID": environment_id,
                "Name": application.ApplicationEnvironment.AppName,
                "SupportContact": application.ApplicationEnvironment.EntityJSON.get("SupportContact", "https://support.access-ci.org/help-ticket"),
                "SupportStatus": application.ApplicationEnvironment.EntityJSON.get("SupportStatus", "production"),
                "URL": application.ApplicationEnvironment.EntityJSON.get("URL", None),
                "Validity": validity,
                "Version": application.ApplicationEnvironment.AppVersion,

                # Cider fields
                "Info_GroupID": cider.other_attributes.get("groups", [])[0]["info_groupid"] if len(cider.other_attributes.get("groups", [])) else None,
                "Info_GroupName": cider.other_attributes.get("groups", [])[0]["name"] if len(cider.other_attributes.get("groups", [])) else None,
                "Info_ResourceID": cider.info_resourceid,
                "Info_ResourceName": cider.resource_descriptive_name,
                "Organization_ID": cider.info_siteid,
                "Organization_Name": cider.other_attributes.get("organizations", [])[0]["organization_name"],
            }

            # Build ResourceV4Local entry
            resource_v4_local_entry = {
                "ID": environment_id_hash,
                "Affiliation": "access-ci.org",
                "CatalogMetaURL": "urn:ogf.org:glue2:access-ci.org:catalog:glue2:executable.software",
                "CreationTime": application.ApplicationEnvironment.CreationTime.isoformat(),
                "LocalID": environment_id,
                "LocalType": "GLUE2 Executable Software",
                "LocalURL": f"https://operations-api.access-ci.org/wh2/glue2/v1/software_full/ID/{environment_id}/",
                "Validity": validity,
                "EntityJSON": entity_json,
            }
            resource_v4_local_list_new.append(resource_v4_local_entry)

    payload = {
        # List of items that were added/removed/updated since last run
        # Returns a payload with the above keys
        **compare_dict_lists(
            resource_v4_local_list_old.values(),
            resource_v4_local_list_new,
        ),
    }
    return payload


def compare_dict_lists(
    old_list,
    new_list,
    id_key="LocalID",
    ignore_fields=None,
):
    """
    Compare two lists of dicts with:
    - nested field diff output
    - dot-notation ignore_fields support
    - optimized for large datasets
    - returns only the new value in 'changes'
    """

    if ignore_fields is None:
        ignore_fields = [
            "CreationTime",
            "ID",
            "LocalID",
            "Validity",
            "EntityJSON.CreationTime",
            "EntityJSON.ID",
            "EntityJSON.LocalID",
            "EntityJSON.Validity",
        ]

    ignore_fields = set(ignore_fields)

    # -----------------------------
    # Fast ignore matcher
    # -----------------------------
    def should_ignore(path):
        return any(path == f or path.startswith(f + ".") for f in ignore_fields)

    # -----------------------------
    # Merge a change into a nested dictionary
    # -----------------------------
    def merge_change(d, path_list, value):
        key = path_list[0]
        if len(path_list) == 1:
            d[key] = value  # only new value
        else:
            if key not in d:
                d[key] = {}
            merge_change(d[key], path_list[1:], value)

    # -----------------------------
    # Recursive diff engine
    # -----------------------------
    def deep_diff_nested(old, new, path="", changes=None):
        if changes is None:
            changes = {}

        if old is new:
            return changes

        if type(old) != type(new):
            merge_change(changes, path.split(".") if path else [], new)
            return changes

        if isinstance(old, dict):
            all_keys = old.keys() | new.keys()
            for key in all_keys:
                current_path = f"{path}.{key}" if path else key

                if should_ignore(current_path):
                    continue

                if key not in old:
                    merge_change(changes, current_path.split("."), new[key])
                elif key not in new:
                    merge_change(changes, current_path.split("."), None)
                else:
                    deep_diff_nested(old[key], new[key], current_path, changes)

            return changes

        if isinstance(old, list):
            if len(old) != len(new):
                merge_change(changes, path.split(".") if path else [], new)
                return changes
            for idx, (o, n) in enumerate(zip(old, new)):
                deep_diff_nested(o, n, f"{path}[{idx}]", changes)
            return changes

        # Primitive values
        if old != new:
            merge_change(changes, path.split(".") if path else [], new)

        return changes

    # -----------------------------
    # Lookup dicts for fast O(n) matching
    # -----------------------------
    old_dict = {item[id_key]: item for item in old_list}
    new_dict = {item[id_key]: item for item in new_list}

    old_ids = set(old_dict)
    new_ids = set(new_dict)

    added = [new_dict[_id] for _id in new_ids - old_ids]
    removed = list(old_ids - new_ids)

    updated = []
    for _id in old_ids & new_ids:
        changes = deep_diff_nested(old_dict[_id], new_dict[_id])
        if changes:
            updated.append({
                "LocalID": _id,
                "changes": changes
            })

    return {
        "added": added,
        "removed": removed,
        "updated": updated
    }
