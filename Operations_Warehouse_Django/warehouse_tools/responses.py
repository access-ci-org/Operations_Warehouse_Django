from rest_framework import status
from rest_framework.response import Response

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
