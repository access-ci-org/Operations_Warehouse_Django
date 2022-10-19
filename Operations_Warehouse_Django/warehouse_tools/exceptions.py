from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
import logging
mylogger = logging.getLogger('warehouse.logger')

class ProcessingException(Exception):
    def __init__(self, response, status):
        self.response = response
        self.status = status
        mylogger.error('%s status=%s (%s)' % (type(self).__name__, repr(self.status), repr(self.response)))
    def __str__(self):
        return repr(self.status)

class MyAPIException(APIException):
    def __init__(self, code=None, detail=None, template_name=None):
        self.status_code = code
        self.detail = {'status_code': code or 'UNKNOWN'}
        if detail:
            self.detail['detail'] = detail
        if template_name is None:
            if code == status.HTTP_400_BAD_REQUEST:
                self.template_name = '400.html'
            elif code == status.HTTP_404_NOT_FOUND:
                self.template_name = '404.html'
            else:
                self.template_name = '500.html'
        Response(self.detail, status=self.status_code, template_name=self.template_name)
