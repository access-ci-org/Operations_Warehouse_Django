from django.shortcuts import render
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer

from warehouse_tools.exceptions import MyAPIException
from warehouse_tools.responses import MyAPIResponse, CustomPagePagination

from .models import *
from .serializers import *
# Create your views here.

class Allocations_v1_fos_List(ListAPIView):
    '''
        Field of Science list
        
        Optional response argument(s):
        ```
            sort=<field>                    (disables hierarchy=true)

        ```
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer,)
    serializer_class = Allocations_fos_DetailURL_Serializer
    @extend_schema(parameters=[
            OpenApiParameter('search_strings', str, OpenApiParameter.QUERY),
            OpenApiParameter('format', str, OpenApiParameter.QUERY),
            OpenApiParameter('sort', str, OpenApiParameter.QUERY),
            OpenApiParameter('hierarchy', bool, OpenApiParameter.QUERY),
            OpenApiParameter('inactive', bool, OpenApiParameter.QUERY)
        ])
    def get(self, request, format=None, **kwargs):
        arg_strings = request.GET.get('search_strings', None)
        if arg_strings:
            want_strings = list(arg_strings.replace(',', ' ').lower().split())
        else:
            want_strings = list()

        arg_hierarchy = request.GET.get('hierarchy', None)
        if arg_hierarchy and arg_hierarchy != '':
            want_hierarchy = True
        else:
            want_hierarchy = False

        arg_inactive = request.GET.get('inactive', None)
        if arg_inactive and arg_inactive != '':
            want_inactive = True
        else:
            want_inactive = False

        if 'parentid' in self.kwargs:
            try:
                objects = FieldOfScience.objects.filter(parent_field_of_science_id__exact=self.kwargs['parentid'])
            except FieldOfScience.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified Parent ID not found')
        elif want_strings:
            try:
                objects = FieldOfScience.objects.filter(field_of_science_desc__icontains=want_strings[0])
                for another in want_strings[1:]:
                    objects = objects.filter(field_of_science_desc__icontains=another)
            except:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Unexpected error handling search_strings')
        else:
            try:
                objects = FieldOfScience.objects.all()
            except:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Fields of Science not found')
        if not want_inactive:
            objects = objects.filter(is_active=True)

        sort_by = request.GET.get('sort')
        if sort_by:
            objects = objects.order_by(sort_by)

        serializer = Allocations_fos_DetailURL_Serializer(objects, context={'request': request}, many=True)

        reqformat = format or request.GET.get('format', None)
        if reqformat == 'json' or sort_by or not want_hierarchy:
            response_obj = {'results': serializer.data}
            return MyAPIResponse(response_obj, template_name='allocations/fos_list.html')

        if not sort_by and want_hierarchy:
            # 1. Create description and parent lookup dictionaries
            desc_lookup = {}
            parent_lookup = {}
            for item in serializer.data:
                desc_lookup[item['field_of_science_id']] = item['field_of_science_desc']
                parent_lookup[item['field_of_science_id']] = item['parent_field_of_science_id']
            # 2. Create sort and depth lookup maps
            sort_map = {}   # The textual field we will sort by
            depth_map = {}  # Distance to an item without a parent
            for item in serializer.data:
                self.build_sort_depth(item['field_of_science_id'], sort_map, depth_map, desc_lookup, parent_lookup)
        
        response_list = list()
        for item in serializer.data:
            response_item = dict(item)
            response_item['sort'] = sort_map[item['field_of_science_id']]
            if depth_map[item['field_of_science_id']] == 0:
                prefix = ''
            else:
                prefix = (depth_map[item['field_of_science_id']] * 4) * '&nbsp;'
            response_item['print_desc'] = prefix + item['field_of_science_desc']
            response_list.append(response_item)
            
        response_obj = {'results': sorted(response_list, key=lambda i: i['sort'])}
        return MyAPIResponse(response_obj, template_name='allocations/fos_list.html')

    def build_sort_depth(self, myid, sm, dm, dl, pl):
        if pl[myid] is None or pl[myid] == '':
            # I don't have a parent, use my own description, depth is 0
            sm[myid] = dl[myid]
            dm[myid] = 0
            return
        if pl[myid] not in sm:
            # My parent doesn't have an SL, iterate to get it
            self.build_sort_depth(pl[myid], sm, dm, dl, pl)
        # Append my parent SL with my own description, increment depth
        sm[myid] = sm[pl[myid]] + ':' + dl[myid]
        dm[myid] = dm[pl[myid]] + 1

class Allocations_v1_fos_Detail(GenericAPIView):
    '''
        Field of Science detail
        
        Optional response argument(s):
        ```
            format={json,html}              (json default)
        ```
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,TemplateHTMLRenderer,)
    serializer_class = Allocations_fos_Serializer
    def get(self, request, format=None, **kwargs):
        returnformat = request.query_params.get('format', 'json')
        if not 'id' in self.kwargs:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Missing ID argument')

        try:
            objects = [FieldOfScience.objects.get(pk=self.kwargs['id'])]
        except FieldOfScience.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified FOS ID not found')
        serializer = Allocations_fos_Serializer(objects, many=True)
        response_obj = {'results': serializer.data}
        return MyAPIResponse(response_obj, template_name='allocations/fos_detail.html')

