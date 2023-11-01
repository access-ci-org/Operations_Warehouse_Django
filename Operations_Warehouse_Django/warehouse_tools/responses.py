from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.utils.urls import replace_query_param
from warehouse_tools.exceptions import MyAPIException

def MyAPIResponse(data, code=None, template_name=None):
    if data is None:
        my_data = {}
    else:
        my_data = data
    status_code = code or status.HTTP_200_OK
    my_data['status_code'] = status_code
    if template_name:
        return Response(my_data, status=status_code, template_name=template_name)
    else:
        return Response(my_data, status=status_code)

class CustomPagePagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    def get_paginated_response(self, data, request, **kwargs):
        # **kwargs are included in the response
        try:
            page = request.GET.get(self.page_query_param)
            if page:
                page = int(page)
                if page == 0:
                    raise
        except:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Pagination page "{}" is not valid'.format(page))
        try:
            page_size = request.GET.get(self.page_size_query_param, api_settings.PAGE_SIZE or 25)
            self.page_size = int(page_size)
        except:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Pagination page_size "{}" is not valid'.format(page_size))
        previous = self.get_previous_link()
        if page == 2:   # Override default behaviour of not returning page=1
            previous = replace_query_param(previous, self.page_query_param, 1)
        return MyAPIResponse({
            'count': self.page.paginator.count,
            'page': page,
            'page_size': self.page_size,
            'next': self.get_next_link(),
            'previous': previous,
            'results': data,
            **kwargs
        })
