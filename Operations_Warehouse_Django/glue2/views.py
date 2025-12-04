import globus_sdk
import requests
from globus_sdk.scopes import GroupsScopes
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from pydantic import ValidationError

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, schema
from rest_framework.generics import UpdateAPIView
from rest_framework.views import APIView
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from cider.filters import CiderInfrastructure_All_Filter
from glue2.models import *
from glue2.serializers import *
from glue2.process import glue2_process_raw_ipf
from resource_v4.models import ResourceV4Local

from warehouse_tools.exceptions import MyAPIException
from warehouse_tools.responses import MyAPIResponse

# Create your views here.

class glue2_process_doc(APIView):
    '''
        Process GLUE2 document entities
    '''
#    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticatedOrReadOnly,)
#    permission_classes = (AllowAny,)
    serializer_class = JSON_Serializer
    def post(self, request, doctype, resourceid, format=None):
        proc = glue2_process_raw_ipf(application='glue2.process', function='glue2_process_doc')
        ts = timezone.now()
        data = next(iter(request.data)) # Get first QueryDict key
        (code, message) = proc.process(ts, doctype, resourceid, data)
        if code is True:
            return Response(message, status=status.HTTP_201_CREATED)
        else:
            return Response(message, status=status.HTTP_400_BAD_REQUEST)

#class AdminDomain_DbList(APIView):
#    '''
#        GLUE2 Administrative Domain entity
#    '''
#    permission_classes = (IsAuthenticatedOrReadOnly,)
#    def get(self, request, format=None):
#        objects = AdminDomain.objects.all()
#        serializer = AdminDomain_DbSerializer(objects, many=True)
#        response_obj = {'results': serializer.data}
#        response_obj['total_results'] = len(objects)
#        return MyAPIResponse(response_obj)
#    def post(self, request, format=None):
#        serializer = AdminDomain_DbSerializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            code = status.HTTP_201_CREATED
#            data = serializer.data
#        else:
#            code = status.HTTP_400_BAD_REQUEST
#            data = serializer.errors
#        return MyAPIResponse({'results': data}, code=code)
#
#
#class AdminDomain_DbDetail(APIView):
#    '''
#        GLUE2 Administrative Domain entity
#    '''
#    # Since Name, AppVersion, and ID may contain a forward slash we use uri_to_iri
#    permission_classes = (IsAuthenticatedOrReadOnly,)
#    def get(self, request, pk, format=None):
#        try:
#            object = AdminDomain.objects.get(pk=uri_to_iri(pk)) # uri_to_iri translates %xx
#        except AdminDomain.DoesNotExist:
#            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
#        serializer = AdminDomain_DbSerializer(object)
#        return MyAPIResponse({'results': [serializer.data]})
#    def put(self, request, pk, format=None):
#        try:
#            object = AdminDomain.objects.get(pk=uri_to_iri(pk))
#        except AdminDomain.DoesNotExist:
#            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
#        serializer = AdminDomain_DbSerializer(object, data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            code = status.HTTP_201_CREATED
#            data = serializer.data
#        else:
#            code = status.HTTP_400_BAD_REQUEST
#            data = serializer.errors
#        return MyAPIResponse({'results': data}, code=code)
#    def delete(self, request, pk, format=None):
#        try:
#            object = AdminDomain.objects.get(pk=uri_to_iri(pk))
#        except AdminDomain.DoesNotExist:
#            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
#        object.delete()
#        return MyAPIResponse(None, code=status.HTTP_204_NO_CONTENT)
#
#class UserDomain_DbList(APIView):
#    '''
#        GLUE2 User Domain entity
#    '''
#    permission_classes = (IsAuthenticatedOrReadOnly,)
#    def get(self, request, format=None):
#        objects = UserDomain.objects.all()
#        serializer = UserDomain_DbSerializer(objects, many=True)
#        response_obj = {'results': serializer.data}
#        response_obj['total_results'] = len(objects)
#        return MyAPIResponse(response_obj)
#    def post(self, request, format=None):
#        serializer = UserDomain_DbSerializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            code = status.HTTP_201_CREATED
#            data = serializer.data
#        else:
#            code = status.HTTP_400_BAD_REQUEST
#            data = serializer.errors
#        return MyAPIResponse({'results': data}, code=code)
#
#class UserDomain_DbDetail(APIView):
#    '''
#        GLUE2 User Domain entity
#    '''
#    # Since Name, AppVersion, and ID may contain a forward slash we use uri_to_iri
#    permission_classes = (IsAuthenticatedOrReadOnly,)
#    def get(self, request, pk, format=None):
#        try:
#            object = UserDomain.objects.get(pk=uri_to_iri(pk)) # uri_to_iri translates %xx
#        except UserDomain.DoesNotExist:
#            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
#        serializer = UserDomain_DbSerializer(object)
#        return MyAPIResponse({'results': [serializer.data]})
#    def put(self, request, pk, format=None):
#        try:
#            object = UserDomain.objects.get(pk=uri_to_iri(pk))
#        except UserDomain.DoesNotExist:
#            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
#        serializer = UserDomain_DbSerializer(object, data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            code = status.HTTP_201_CREATED
#            data = serializer.data
#        else:
#            code = status.HTTP_400_BAD_REQUEST
#            data = serializer.errors
#        return MyAPIResponse({'results': data}, code=code)
#    def delete(self, request, pk, format=None):
#        try:
#            object = UserDomain.objects.get(pk=uri_to_iri(pk))
#        except UserDomain.DoesNotExist:
#            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
#        object.delete()
#        return MyAPIResponse(None, code=status.HTTP_204_NO_CONTENT)
#
#class AccessPolicy_DbList(APIView):
#    '''
#        GLUE2 Access Policy entity
#    '''
#    permission_classes = (IsAuthenticatedOrReadOnly,)
#    def get(self, request, format=None):
#        objects = AccessPolicy.objects.all()
#        serializer = AccessPolicy_DbSerializer(objects, many=True)
#        response_obj = {'results': serializer.data}
#        response_obj['total_results'] = len(objects)
#        return MyAPIResponse(response_obj)
#    def post(self, request, format=None):
#        serializer = AccessPolicy_DbSerializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            code = status.HTTP_201_CREATED
#            data = serializer.data
#        else:
#            code = status.HTTP_400_BAD_REQUEST
#            data = serializer.errors
#        return MyAPIResponse({'results': data}, code=code)
#
#class AccessPolicy_DbDetail(APIView):
#    '''
#        GLUE2 Access Policy entity
#    '''
#    # Since Name, AppVersion, and ID may contain a forward slash we use uri_to_iri
#    permission_classes = (IsAuthenticatedOrReadOnly,)
#    def get(self, request, pk, format=None):
#        try:
#            object = AccessPolicy.objects.get(pk=uri_to_iri(pk)) # uri_to_iri translates %xx
#        except AccessPolicy.DoesNotExist:
#            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
#        serializer = AccessPolicy_DbSerializer(object)
#        return MyAPIResponse({'results': [serializer.data]})
#    def put(self, request, pk, format=None):
#        try:
#            object = AccessPolicy.objects.get(pk=uri_to_iri(pk))
#        except AccessPolicy.DoesNotExist:
#            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
#        serializer = AccessPolicy_DbSerializer(object, data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            code = status.HTTP_201_CREATED
#            data = serializer.data
#        else:
#            code = status.HTTP_400_BAD_REQUEST
#            data = serializer.errors
#        return MyAPIResponse({'results': data}, code=code)
#    def delete(self, request, pk, format=None):
#        try:
#            object = AccessPolicy.objects.get(pk=uri_to_iri(pk))
#        except AccessPolicy.DoesNotExist:
#            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
#        object.delete()
#        return MyAPIResponse(None, code=status.HTTP_204_NO_CONTENT)
#
#class Contact_DbList(APIView):
#    '''
#        GLUE2 Contact entity
#    '''
#    permission_classes = (IsAuthenticatedOrReadOnly,)
#    def get(self, request, format=None):
#        objects = Contact.objects.all()
#        serializer = Contact_DbSerializer(objects, many=True)
#        response_obj = {'results': serializer.data}
#        response_obj['total_results'] = len(objects)
#        return MyAPIResponse(response_obj)
#    def post(self, request, format=None):
#        serializer = Contact_DbSerializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            code = status.HTTP_201_CREATED
#            data = serializer.data
#        else:
#            code = status.HTTP_400_BAD_REQUEST
#            data = serializer.errors
#        return MyAPIResponse({'results': data}, code=code)
#
#class Contact_DbDetail(APIView):
#    '''
#        GLUE2 Contact entity
#    '''
#    # Since Name, AppVersion, and ID may contain a forward slash we use uri_to_iri
#    permission_classes = (IsAuthenticatedOrReadOnly,)
#    def get(self, request, pk, format=None):
#        try:
#            object = Contact.objects.get(pk=uri_to_iri(pk)) # uri_to_iri translates %xx
#        except Contact.DoesNotExist:
#            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
#        serializer = Contact_DbSerializer(object)
#        return MyAPIResponse({'results': [serializer.data]})
#    def put(self, request, pk, format=None):
#        try:
#            object = Contact.objects.get(pk=uri_to_iri(pk))
#        except Contact.DoesNotExist:
#            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
#        serializer = Contact_DbSerializer(object, data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            code = status.HTTP_201_CREATED
#            data = serializer.data
#        else:
#            code = status.HTTP_400_BAD_REQUEST
#            data = serializer.errors
#        return MyAPIResponse({'results': data}, code=code)
#    def delete(self, request, pk, format=None):
#        try:
#            object = Contact.objects.get(pk=uri_to_iri(pk))
#        except Contact.DoesNotExist:
#            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
#        object.delete()
#        return MyAPIResponse(None, code=status.HTTP_204_NO_CONTENT)
#
#class Location_DbList(APIView):
#    '''
#        GLUE2 Location entity
#    '''
#    permission_classes = (IsAuthenticatedOrReadOnly,)
#    def get(self, request, format=None):
#        objects = Location.objects.all()
#        serializer = Location_DbSerializer(objects, many=True)
#        return Response(serializer.data)
#    def post(self, request, format=None):
#        serializer = Location_DbSerializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data, status=status.HTTP_201_CREATED)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#class Location_DbDetail(APIView):
#    '''
#        GLUE2 Location entity
#    '''
#    permission_classes = (IsAuthenticatedOrReadOnly,)
#    def get(self, request, pk, format=None):
#        try:
#            object = Location.objects.get(pk=pk)
#        except Location.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        serializer = Location_DbSerializer(object)
#        return Response(serializer.data)
#    def put(self, request, pk, format=None):
#        try:
#            object = Location.objects.get(pk=pk)
#        except Location.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        serializer = Location_DbSerializer(object, data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#    def delete(self, request, pk, format=None):
#        try:
#            object = Location.objects.get(pk=pk)
#        except Location.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        object.delete()
#        return Response(status=status.HTTP_204_NO_CONTENT)
#
#
#class ApplicationEnvironment_DbList(APIView):
#    '''
#        GLUE2 Application Environment entity
#    '''
#    permission_classes = (IsAuthenticatedOrReadOnly,)
#    def get(self, request, format=None):
#        objects = ApplicationEnvironment.objects.all()
#        serializer = ApplicationEnvironment_DbSerializer(objects, many=True)
#        return Response(serializer.data)
#    def post(self, request, format=None):
#        serializer = ApplicationEnvironment_DbSerializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data, status=status.HTTP_201_CREATED)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#class ApplicationEnvironment_DbDetail(APIView):
#    '''
#        GLUE2 Application Environment entity
#    '''
#    # Since Name, AppVersion, and ID may contain a forward slash we use uri_to_iri
#    permission_classes = (IsAuthenticatedOrReadOnly,)
#    def get(self, request, pk, format=None):
#        try:
#            object = ApplicationEnvironment.objects.get(pk=uri_to_iri(pk)) # uri_to_iri translates %xx
#        except ApplicationEnvironment.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        return Response(ApplicationEnvironment_DbSerializer(object).data)
#    def put(self, request, pk, format=None):
#        try:
#            object = ApplicationEnvironment.objects.get(pk=uri_to_iri(pk))
#        except ApplicationEnvironment.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        serializer = ApplicationEnvironment_DbSerializer(object, data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#    def delete(self, request, pk, format=None):
#        try:
#            object = ApplicationEnvironment.objects.get(pk=uri_to_iri(pk))
#        except ApplicationEnvironment.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        object.delete()
#        return Response(status=status.HTTP_204_NO_CONTENT)
#
#class ApplicationHandle_DbList(APIView):
#    '''
#        GLUE2 Application Handle entity
#    '''
#    # Since Name, Value, and ID may contain a forward slash we use uri_to_iri
#    permission_classes = (IsAuthenticatedOrReadOnly,)
#    def get(self, request, format=None):
#        objects = ApplicationHandle.objects.all()
##        serializer = ApplicationHandle_DbSerializer(objects, many=True, context={'request', request})
#        serializer = ApplicationHandle_DbSerializer(objects, many=True)
#        return Response(serializer.data)
#    def post(self, request, format=None):
#        serializer = ApplicationHandle_DbSerializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data, status=status.HTTP_201_CREATED)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#class ApplicationHandle_DbDetail(APIView):
#    '''
#        GLUE2 Application Handle entity
#    '''
#    permission_classes = (IsAuthenticatedOrReadOnly,)
#    def get(self, request, pk, format=None):
#        try:
#            object = ApplicationHandle.objects.get(pk=uri_to_iri(pk))
#        except ApplicationHandle.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
##        serializer = ApplicationHandle_DbSerializer(object, context={'request', request})
#        return Response(ApplicationHandle_DbSerializer(object).data)
#    def put(self, request, pk, format=None):
#        try:
#            object = ApplicationHandle.objects.get(pk=uri_to_iri(pk))
#        except ApplicationHandle.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        serializer = ApplicationHandle_DbSerializer(object, data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#    def delete(self, request, pk, format=None):
#        try:
#            object = ApplicationHandle.objects.get(pk=uri_to_iri(pk))
#        except ApplicationHandle.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        object.delete()
#        return Response(status=status.HTTP_204_NO_CONTENT)
#
#class AbstractService_DbList(APIView):
#    '''
#        GLUE2 Abstract Service entity
#    '''
#    permission_classes = (IsAuthenticatedOrReadOnly,)
#    def get(self, request, format=None):
#        objects = AbstractService.objects.all()
#        serializer = AbstractService_DbSerializer(objects, many=True)
#        return Response(serializer.data)
#    def post(self, request, format=None):
#        serializer = AbstractService_DbSerializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data, status=status.HTTP_201_CREATED)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#class AbstractService_DbDetail(APIView):
#    '''
#        GLUE2 Abstract Service entity
#    '''
#    permission_classes = (IsAuthenticatedOrReadOnly,)
#    def get(self, request, pk, format=None):
#        try:
#            object = AbstractService.objects.get(pk=pk)
#        except AbstractService.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        serializer = AbstractService_DbSerializer(object)
#        return Response(serializer.data)
#    def put(self, request, pk, format=None):
#        try:
#            object = AbstractService.objects.get(pk=pk)
#        except AbstractService.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        serializer = AbstractService_DbSerializer(object, data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#    def delete(self, request, pk, format=None):
#        try:
#            object = AbstractService.objects.get(pk=pk)
#        except AbstractService.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        object.delete()
#        return Response(status=status.HTTP_204_NO_CONTENT)
#
#class Endpoint_DbList(APIView):
#    '''
#        GLUE2 Endpoint entity
#    '''
#    permission_classes = (IsAuthenticatedOrReadOnly,)
#    def get(self, request, format=None):
#        objects = Endpoint.objects.all()
#        serializer = Endpoint_DbSerializer(objects, many=True)
#        return Response(serializer.data)
#    def post(self, request, format=None):
#        serializer = Endpoint_DbSerializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data, status=status.HTTP_201_CREATED)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#class Endpoint_DbDetail(APIView):
#    '''
#        GLUE2 Endpoint entity
#    '''
#    permission_classes = (IsAuthenticatedOrReadOnly,)
#    def get(self, request, pk, format=None):
#        try:
#            object = Endpoint.objects.get(pk=pk)
#        except Endpoint.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        serializer = Endpoint_DbSerializer(object)
#        return Response(serializer.data)
#    def put(self, request, pk, format=None):
#        try:
#            object = Endpoint.objects.get(pk=pk)
#        except Endpoint.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        serializer = Endpoint_DbSerializer(object, data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#    def delete(self, request, pk, format=None):
#        try:
#            object = Endpoint.objects.get(pk=pk)
#        except Endpoint.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        object.delete()
#        return Response(status=status.HTTP_204_NO_CONTENT)

class ComputingManager_DbList(APIView):
    '''
        GLUE2 Computing Manager entity
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ComputingManager_Serializer
    def get(self, request, format=None):
        objects = ComputingManager.objects.all()
        serializer = ComputingManager_Serializer(objects, many=True)
        return Response(serializer.data)
#    def post(self, request, format=None):
#        serializer = ComputingManager_Serializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data, status=status.HTTP_201_CREATED)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ComputingManager_DbDetail(APIView):
    '''
        GLUE2 Computing Manager entity
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ComputingManager_Serializer
    def get(self, request, pk, format=None):
        try:
            object = ComputingManager.objects.get(pk=pk)
        except ComputingManager.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ComputingManager_Serializer(object)
        return Response(serializer.data)
#    def put(self, request, pk, format=None):
#        try:
#            object = ComputingManager.objects.get(pk=pk)
#        except ComputingManager.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        serializer = ComputingManager_Serializer(object, data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#    def delete(self, request, pk, format=None):
#        try:
#            object = ComputingManager.objects.get(pk=pk)
#        except ComputingManager.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        object.delete()
#        return Response(status=status.HTTP_204_NO_CONTENT)

class ExecutionEnvironment_DbList(APIView):
    '''
        GLUE2 Execution Environment entity
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ExecutionEnvironment_Serializer
    def get(self, request, format=None):
        objects = ExecutionEnvironment.objects.all()
        serializer = ExecutionEnvironment_Serializer(objects, many=True)
        return Response(serializer.data)
#    def post(self, request, format=None):
#        serializer = ExecutionEnvironment_DbSerializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data, status=status.HTTP_201_CREATED)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExecutionEnvironment_DbDetail(APIView):
    '''
        GLUE2 Execution Environment entity
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ExecutionEnvironment_Serializer
    def get(self, request, pk, format=None):
        try:
            object = ExecutionEnvironment.objects.get(pk=pk)
        except ExecutionEnvironment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ExecutionEnvironment_Serializer(object)
        return Response(serializer.data)
#    def put(self, request, pk, format=None):
#        try:
#            object = ExecutionEnvironment.objects.get(pk=pk)
#        except ExecutionEnvironment.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        serializer = ExecutionEnvironment_DbSerializer(object, data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#    def delete(self, request, pk, format=None):
#        try:
#            object = ExecutionEnvironment.objects.get(pk=pk)
#        except ExecutionEnvironment.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        object.delete()
#        return Response(status=status.HTTP_204_NO_CONTENT)

class ComputingShare_DbList(APIView):
    '''
        GLUE2 Computing Share entity
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ComputingShare_Serializer
    def get(self, request, format=None):
        objects = ComputingShare.objects.all()
        serializer = ComputingShare_Serializer(objects, many=True)
        return Response(serializer.data)
#    def post(self, request, format=None):
#        serializer = ComputingShare_DbSerializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data, status=status.HTTP_201_CREATED)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ComputingShare_DbDetail(APIView):
    '''
        GLUE2 Computing Share entity
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ComputingShare_Serializer
    def get(self, request, pk, format=None):
        try:
            object = ComputingShare.objects.get(pk=pk)
        except ComputingShare.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ComputingShare_Serializer(object)
        return Response(serializer.data)
#    def put(self, request, pk, format=None):
#        try:
#            object = ComputingShare.objects.get(pk=pk)
#        except ComputingShare.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        serializer = ComputingShare_DbSerializer(object, data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#    def delete(self, request, pk, format=None):
#        try:
#            object = ComputingShare.objects.get(pk=pk)
#        except ComputingShare.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        object.delete()
#        return Response(status=status.HTTP_204_NO_CONTENT)

class ComputingQueue_DbList(APIView):
    '''
        GLUE2 Computing Queue entity
    '''
    permission_classes = (IsAuthenticated,)
    authentication_classes = (BasicAuthentication,)
#    authentication_classes = (GlobusAuthentication,)
    serializer_class = ComputingQueue_Serializer
    def get(self, request, format=None, **kwargs):
        if 'resourceid' in self.kwargs:
            try:
                objects = ComputingQueue.objects.filter(ResourceID__exact=self.kwargs['resourceid'])
            except ComputingQueue.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                objects = ComputingQueue.objects.all()
            except ComputingQueue.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ComputingQueue_Serializer(objects, many=True)
        return Response(serializer.data)
#    def post(self, request, format=None):
#        serializer = ComputingQueue_DbSerializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data, status=status.HTTP_201_CREATED)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ComputingQueue_DbDetail(APIView):
    '''
        GLUE2 Computing Queue entity
    '''
    permission_classes = (IsAuthenticated,)
    authentication_classes = (BasicAuthentication,)
#    authentication_classes = (GlobusAuthentication,)
    serializer_class = ComputingQueue_Serializer
    def get(self, request, pk, format=None):
        try:
            object = ComputingQueue.objects.get(pk=pk)
        except ComputingQueue.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ComputingQueue_Serializer(object)
        return Response(serializer.data)
#    def put(self, request, pk, format=None):
#        try:
#            object = ComputingQueue.objects.get(pk=pk)
#        except ComputingQueue.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        serializer = ComputingQueue_DbSerializer(object, data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#    def delete(self, request, pk, format=None):
#        try:
#            object = ComputingQueue.objects.get(pk=pk)
#        except ComputingQueue.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        object.delete()
#        return Response(status=status.HTTP_204_NO_CONTENT)

#class ComputingActivity_DbList(APIView):
#    '''
#        GLUE2 Computing Activity entity
#    '''
#    permission_classes = (IsAuthenticated,)
#    authentication_classes = (GlobusAuthentication,)
#    def get(self, request, format=None):
#        objects = ComputingActivity.objects.all()
#        serializer = ComputingActivity_DbSerializer(objects, many=True)
#        return Response(serializer.data)
#    def post(self, request, format=None):
#        serializer = ComputingActivity_DbSerializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data, status=status.HTTP_201_CREATED)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#class ComputingActivity_DbDetail(APIView):
#    '''
#        GLUE2 Computing Activity entity
#    '''
#    permission_classes = (IsAuthenticated,)
#    authentication_classes = (GlobusAuthentication,)
#    def get(self, request, pk, format=None):
#        try:
#            object = ComputingActivity.objects.get(pk=pk)
#        except ComputingActivity.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        serializer = ComputingActivity_DbSerializer(object)
#        return Response(serializer.data)
#    def put(self, request, pk, format=None):
#        try:
#            object = ComputingActivity.objects.get(pk=pk)
#        except ComputingActivity.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        serializer = ComputingActivity_DbSerializer(object, data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#    def delete(self, request, pk, format=None):
#        try:
#            object = ComputingActivity.objects.get(pk=pk)
#        except ComputingActivity.DoesNotExist:
#            return Response(status=status.HTTP_404_NOT_FOUND)
#        object.delete()
#        return Response(status=status.HTTP_204_NO_CONTENT)

class ComputingManagerAcceleratorInfo_DbList(APIView):
    '''
        GLUE2 Computing Manager Accelerator Information entity
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ComputingManagerAcceleratorInfo_Serializer
    def get(self, request, format=None):
        objects = ComputingManagerAcceleratorInfo.objects.all()
        serializer = ComputingManagerAcceleratorInfo_Serializer(objects, many=True)
        response_obj = {'results': serializer.data}
        response_obj['total_results'] = len(objects)
        return MyAPIResponse(response_obj)
#    def post(self, request, format=None):
#        serializer = ComputingManagerAcceleratorInfo_DbSerializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            code = status.HTTP_201_CREATED
#            data = serializer.data
#        else:
#            code = status.HTTP_400_BAD_REQUEST
#            data = serializer.errors
#        return MyAPIResponse({'results': data}, code=code)
#
class ComputingManagerAcceleratorInfo_DbDetail(APIView):
    '''
        GLUE2 Computing Manager Accelerator Information entity
    '''
    # Since Name, AppVersion, and ID may contain a forward slash we use uri_to_iri
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ComputingManagerAcceleratorInfo_Serializer
    def get(self, request, pk, format=None):
        try:
            object = ComputingManagerAcceleratorInfo.objects.get(pk=uri_to_iri(pk)) # uri_to_iri translates %xx
        except ComputingManagerAcceleratorInfo.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
        serializer = ComputingManagerAcceleratorInfo_Serializer(object)
        return MyAPIResponse({'results': [serializer.data]})
#    def put(self, request, pk, format=None):
#        try:
#            object = ComputingManagerAcceleratorInfo.objects.get(pk=uri_to_iri(pk))
#        except ComputingManagerAcceleratorInfo.DoesNotExist:
#            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
#        serializer = ComputingManagerAcceleratorInfo_DbSerializer(object, data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            code = status.HTTP_201_CREATED
#            data = serializer.data
#        else:
#            code = status.HTTP_400_BAD_REQUEST
#            data = serializer.errors
#        return MyAPIResponse({'results': data}, code=code)
#    def delete(self, request, pk, format=None):
#        try:
#            object = ComputingManagerAcceleratorInfo.objects.get(pk=uri_to_iri(pk))
#        except ComputingManagerAcceleratorInfo.DoesNotExist:
#            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
#        object.delete()
#        return MyAPIResponse(None, code=status.HTTP_204_NO_CONTENT)

class ComputingShareAcceleratorInfo_DbList(APIView):
    '''
        GLUE2 Computing Share Accelerator Information entity
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ComputingShareAcceleratorInfo_Serializer
    def get(self, request, format=None):
        objects = ComputingShareAcceleratorInfo.objects.all()
        serializer = ComputingShareAcceleratorInfo_Serializer(objects, many=True)
        response_obj = {'results': serializer.data}
        response_obj['total_results'] = len(objects)
        return MyAPIResponse(response_obj)
#    def post(self, request, format=None):
#        serializer = ComputingShareAcceleratorInfo_DbSerializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            code = status.HTTP_201_CREATED
#            data = serializer.data
#        else:
#            code = status.HTTP_400_BAD_REQUEST
#            data = serializer.errors
#        return MyAPIResponse({'results': data}, code=code)

class ComputingShareAcceleratorInfo_DbDetail(APIView):
    '''
        GLUE2 Computing Share Accelerator Information entity
    '''
    # Since Name, AppVersion, and ID may contain a forward slash we use uri_to_iri
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ComputingShareAcceleratorInfo_Serializer
    def get(self, request, pk, format=None):
        try:
            object = ComputingShareAcceleratorInfo.objects.get(pk=uri_to_iri(pk)) # uri_to_iri translates %xx
        except ComputingShareAcceleratorInfo.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
        serializer = ComputingShareAcceleratorInfo_Serializer(object)
        return MyAPIResponse({'results': [serializer.data]})
#    def put(self, request, pk, format=None):
#        try:
#            object = ComputingShareAcceleratorInfo.objects.get(pk=uri_to_iri(pk))
#        except ComputingShareAcceleratorInfo.DoesNotExist:
#            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
#        serializer = ComputingShareAcceleratorInfo_DbSerializer(object, data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            code = status.HTTP_201_CREATED
#            data = serializer.data
#        else:
#            code = status.HTTP_400_BAD_REQUEST
#            data = serializer.errors
#        return MyAPIResponse({'results': data}, code=code)
#    def delete(self, request, pk, format=None):
#        try:
#            object = ComputingShareAcceleratorInfo.objects.get(pk=uri_to_iri(pk))
#        except ComputingShareAcceleratorInfo.DoesNotExist:
#            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
#        object.delete()
#        return MyAPIResponse(None, code=status.HTTP_204_NO_CONTENT)

class AcceleratorEnvironment_DbList(APIView):
    '''
        GLUE2 Accelerator Environment entity
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = AcceleratorEnvironment_Serializer
    def get(self, request, format=None):
        objects = AcceleratorEnvironment.objects.all()
        serializer = AcceleratorEnvironment_Serializer(objects, many=True)
        response_obj = {'results': serializer.data}
        response_obj['total_results'] = len(objects)
        return MyAPIResponse(response_obj)
#    def post(self, request, format=None):
#        serializer = AcceleratorEnvironement_Serializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            code = status.HTTP_201_CREATED
#            data = serializer.data
#        else:
#            code = status.HTTP_400_BAD_REQUEST
#            data = serializer.errors
#        return MyAPIResponse({'results': data}, code=code)

class AcceleratorEnvironment_DbDetail(APIView):
    '''
        GLUE2 Accelerator Environment entity
    '''
    # Since Name, AppVersion, and ID may contain a forward slash we use uri_to_iri
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = AcceleratorEnvironment_Serializer
    def get(self, request, pk, format=None):
        try:
            object = AcceleratorEnvironment.objects.get(pk=uri_to_iri(pk)) # uri_to_iri translates %xx
        except AcceleratorEnvironment.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
        serializer = AcceleratorEnvironment_Serializer(object)
        return MyAPIResponse({'results': [serializer.data]})
#    def put(self, request, pk, format=None):
#        try:
#            object = AcceleratorEnvironment.objects.get(pk=uri_to_iri(pk))
#        except AcceleratorEnvironment.DoesNotExist:
#            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
#        serializer = AcceleratorEnvironement_Serializer(object, data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            code = status.HTTP_201_CREATED
#            data = serializer.data
#        else:
#            code = status.HTTP_400_BAD_REQUEST
#            data = serializer.errors
#        return MyAPIResponse({'results': data}, code=code)
#    def delete(self, request, pk, format=None):
#        try:
#            object = AcceleratorEnvironment.objects.get(pk=uri_to_iri(pk))
#        except AcceleratorEnvironment.DoesNotExist:
#            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Not found')
#        object.delete()
#        return MyAPIResponse(None, code=status.HTTP_204_NO_CONTENT)

#class EntityHistory_DbList(APIView):
#    '''
#        ### GLUE2 entityhistory search and list
#
#        Optional selection argument(s):
#        ```
#            start_date=<yyyy-mm-dd>
#            end_date=<yyyy-mm-dd>
#            resourceid=<resourceid>
#        ```
#        Optional response argument(s):
#        ```
#            fields=__usage__                    (return three fields for usage analysis)
#            format={json,xml,html}              (json default)
#        ```
#        .
#    '''
#    permission_classes = (IsAuthenticatedOrReadOnly,)
#    def get(self, request, format=None, **kwargs):
#        if 'doctype' not in self.kwargs:
#            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Missing /doctype/.. argument')
#        arg_doctype = kwargs['doctype']
#
#        try:
#            dt = request.GET.get('start_date', None)
#            pdt = parse_datetime(dt)
#            if pdt is None: # If it was only a date try adding the time
#                pdt = parse_datetime(dt + 'T00:00:00.0+00:00')
#            if pdt is None:
#                raise Exception
#            arg_startdate = pdt.astimezone(UTC).strftime('%Y-%m-%dT%H:%M:%S%z')
#        except:
#            arg_startdate = None
#
#        try:
#            dt = request.GET.get('end_date', None)
#            pdt = parse_datetime(dt)
#            if pdt is None: # If it was only a date try adding the time
#                pdt = parse_datetime(dt + 'T23:59:59.0+00:00')
#            if pdt is None:
#                raise Exception
#            arg_enddate = (pdt.astimezone(UTC) + timedelta(seconds=1)).strftime('%Y-%m-%dT%H:%M:%S%z')
#        except:
#            arg_enddate = None
#
#        arg_resourceid = request.GET.get('resourceid', None)
#
#        arg_fields = request.GET.get('fields', None)
#        if arg_fields:
#            want_fields = set(arg_fields.lower().split(','))
#        else:
#            want_fields = set()
#
#        objects = EntityHistory.objects.filter(DocumentType=arg_doctype)
#
#        if arg_resourceid:
#            objects = objects.filter(ResourceID=arg_resourceid)             # String Comparison
#        if arg_startdate:
#            objects = objects.filter(ReceivedTime__gte=arg_startdate)       # String Comparison
#        if arg_enddate:
#            objects = objects.filter(ReceivedTime__lt=arg_enddate)         # String Comparison
#
#        if '__usage__' in want_fields:
#            serializer = EntityHistory_Usage_Serializer(objects, many=True)
#        else:
#            serializer = EntityHistory_Serializer(objects, many=True)
#        response_obj = {'results': serializer.data}
#        response_obj['total_results'] = len(objects)
#        return MyAPIResponse(response_obj)
#
#    def post(self, request, format=None):
#        serializer = EntityHistory_Serializer(data=request.data)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data, status=status.HTTP_201_CREATED)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EntityHistory_DbDetail(APIView):
    '''
        GLUE2 received entity history
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = EntityHistory_Serializer
    def get(self, request, id, format=None):
        try:
            object = EntityHistory.objects.get(pk=id)
        except EntityHistory.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = EntityHistory_Serializer(object)
        return Response(serializer.data)

##############
# Software information comes from ApplicationHandle and the related ApplicationEnvironment
class Software_List(APIView):
    '''
        GLUE2 software combining ApplicationEnvironment and AppliactionHandle
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ApplicationHandle_Serializer
    def get(self, request, format=None):
        objects = ApplicationHandle.objects.all()
        serializer = ApplicationHandle_Serializer(objects, many=True)
        return Response(serializer.data)

class Software_Detail(APIView):
    '''
        GLUE2 software combining ApplicationEnvironment and AppliactionHandle
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    renderer_classes = (JSONRenderer,)
    serializer_class = ApplicationHandle_Serializer
    def get(self, request, format=None, **kwargs):
        if 'id' in self.kwargs:
            try:
                object = ApplicationHandle.objects.get(pk=uri_to_iri(self.kwargs['id'])) # uri_to_iri translates %xx
            except ApplicationHandle.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = ApplicationHandle_Serializer(object)
        elif 'resourceid' in self.kwargs:
            objects = ApplicationHandle.objects.filter(ResourceID__exact=self.kwargs['resourceid'])
            serializer = ApplicationHandle_Serializer(objects, many=True)
        elif 'appname' in self.kwargs:
            objects = ApplicationHandle.objects.filter(ApplicationEnvironment__AppName__exact=uri_to_iri(self.kwargs['appname']))
            serializer = ApplicationHandle_Serializer(objects, many=True)
        return Response(serializer.data)

class Software_Full(APIView):
    '''
        GLUE2 Software detailed information ApplicationHandle, ApplicationEnvironment, ...
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = Software_Community_Serializer
    def get(self, request, format=None, **kwargs):
        if 'id' in self.kwargs:
            try:
                object = ApplicationHandle.objects.get(pk=uri_to_iri(self.kwargs['id'])) # uri_to_iri translates %xx
            except ApplicationHandle.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = Software_Community_Serializer(object)
        elif 'resourceid' in self.kwargs:
            objects = ApplicationHandle.objects.filter(ResourceID__exact=self.kwargs['resourceid'])
            serializer = Software_Community_Serializer(objects, many=True)
        elif 'appname' in self.kwargs:
            objects = ApplicationHandle.objects.filter(ApplicationEnvironment__AppName__exact=uri_to_iri(self.kwargs['appname']))
            serializer = Software_Community_Serializer(objects, many=True)
        else:
            objects = ApplicationHandle.objects.all()
            serializer = Software_Community_Serializer(objects, many=True)
        return MyAPIResponse({'results': serializer.data})

class Software_Fast(APIView):
    '''
        GLUE2 Software detailed information from ApplicationHandle and ApplicationEnvironment, ...
        FAST serialization designed for download
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = None
    def get(self, request, format=None, **kwargs):
        cider = CiderInfrastructure_All_Filter(type='Compute')
        site_lookup = { item.info_resourceid: item.info_siteid for item in cider }
        objects = ApplicationHandle.objects.all().select_related('ApplicationEnvironment')
        output = [ Serialize_Software(object, site_lookup) for object in objects ]
#        serializer = Software_Fast_Serializer(objects, many=True)
#        return MyAPIResponse({'results': serializer.data})
        return MyAPIResponse({'results': output})

# Service information comes from Endpoint and the parent AbstractService
class Services_List(APIView):
    '''
        GLUE2 services combining AbstractService and Endpoint
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = EndpointServices_Support_Serializer
    def get(self, request, format=None):
        objects = Endpoint.objects.all()
        serializer = EndpointServices_Support_Serializer(objects, many=True)
        return Response(serializer.data)

class Services_Detail(APIView):
    '''
        GLUE2 services combining AbstractService and Endpoint
    '''
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = EndpointServices_Serializer
    def get(self, request, format=None, **kwargs):
        if 'id' in self.kwargs:
            try:
                object = Endpoint.objects.get(pk=self.kwargs['id'])
            except Endpoint.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = EndpointServices_Serializer(object)
        elif 'resourceid' in self.kwargs:
            objects = Endpoint.objects.filter(ResourceID__exact=self.kwargs['resourceid'])
            serializer = EndpointServices_Serializer(objects, many=True)
        elif 'interfacename' in self.kwargs:
            objects = Endpoint.objects.filter(InterfaceName__exact=self.kwargs['interfacename'])
            serializer = EndpointServices_Serializer(objects, many=True)
        elif 'servicetype' in self.kwargs:
            objects = Endpoint.objects.filter(AbstractService__ServiceType__exact=self.kwargs['servicetype'])
            serializer = EndpointServices_Serializer(objects, many=True)
        return Response(serializer.data)

class Jobqueue_List(APIView):
    '''
        GLUE2 Jobs Queue from ComputingQueue
    '''
    permission_classes = (IsAuthenticated,)
    authentication_classes = (BasicAuthentication,)
#    authentication_classes = (GlobusAuthentication,)
    renderer_classes = (JSONRenderer,TemplateHTMLRenderer,)
    serializer_class = ComputingQueue_Expand_Serializer
    def get(self, request, format=None, **kwargs):
        if 'resourceid' in self.kwargs:
            try:
                objects = ComputingQueue.objects.filter(ResourceID__exact=self.kwargs['resourceid'])
            except ComputingQueue.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='ResourceID not found')
        else:
            objects = ComputingQueue.objects.all()
        try:
            sort_by = request.GET.get('sort')
        except:
            sort_by = None
        serializer = ComputingQueue_Expand_Serializer(objects, many=True, context={'sort_by': sort_by})
        return MyAPIResponse({'result_set': serializer.data}, template_name='glue2_views_api/jobqueues.html')

class Job_Detail(APIView):
    '''
        GLUE2 Job Detail from ComputingActivity
    '''
    permission_classes = (IsAuthenticated,)
#    authentication_classes = (GlobusAuthentication,)
    renderer_classes = (JSONRenderer,TemplateHTMLRenderer,)
    serializer_class = ComputingActivity_Expand_Serializer
    def get(self, request, format=None, **kwargs):
        if 'id' in self.kwargs:
            try:
                object = ComputingActivity.objects.get(pk=self.kwargs['id'])
            except ComputingActivity.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='ID not found')
        else:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Invalid request')
        serializer = ComputingActivity_Expand_Serializer(object)
        return MyAPIResponse({'result_set': [serializer.data]}, template_name='glue2_views_api/job_detail.html')

class Job_List(APIView):
    '''
        GLUE2 Jobs from ComputingActivity
    '''
    permission_classes = (IsAuthenticated,)
#    authentication_classes = (GlobusAuthentication,)
    renderer_classes = (JSONRenderer,TemplateHTMLRenderer,)
    serializer_class = ComputingActivity_Expand_Serializer
    def get(self, request, format=None, **kwargs):
        if 'id' in self.kwargs:
            try:
                objects = [ComputingActivity.objects.get(pk=self.kwargs['id'])]
            except ComputingActivity.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='ID not found')
        elif 'resourceid' in self.kwargs and 'queue' in self.kwargs:
            try:
                objects = ComputingActivity.objects.filter(ResourceID__exact=self.kwargs['resourceid']).filter(EntityJSON__Queue__exact=self.kwargs['queue'])
            except ComputingActivity.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='ResourceID and Queue not found')
        elif 'resourceid' in self.kwargs and 'localaccount' in self.kwargs:
            try:
                objects = ComputingActivity.objects.filter(ResourceID__exact=self.kwargs['resourceid']).filter(EntityJSON__LocalOwner__exact=self.kwargs['localaccount'])
            except ComputingActivity.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='ResourceID and LocalAccount not found')
        elif 'resourceid' in self.kwargs:
            try:
                objects = ComputingActivity.objects.filter(ResourceID__exact=self.kwargs['resourceid'])
            except ComputingActivity.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='ResourceID not found')
        else:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Invalid request')
        serializer = ComputingActivity_Expand_Serializer(objects, many=True, context={'request': request})
        return MyAPIResponse({'result_set': serializer.data}, template_name='glue2_views_api/jobs.html')

class Jobs_per_Resource_by_ProfileID(APIView):
    '''
        GLUE2 Jobs from ComputingActivity
    '''
    permission_classes = (IsAuthenticated,)
#    authentication_classes = (GlobusAuthentication,)
    renderer_classes = (JSONRenderer,TemplateHTMLRenderer,)
    serializer_class = ComputingActivity_Expand_Serializer
    def get(self, request, format=None, **kwargs):
        fullusername = None
        username = None
        if request.user.is_authenticated:
            fullusername = request.user.username
            username = fullusername[:fullusername.rfind("@")]

        if 'resourceid' in self.kwargs:
            try:
                localaccount = XSEDELocalUsermap.objects.get(ResourceID=self.kwargs['resourceid'],portal_login=username)
            except XSEDELocalUsermap.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='User not found in user database')
            try:
                    objects = ComputingActivity.objects.filter(ResourceID__exact=self.kwargs['resourceid']).filter(EntityJSON__LocalOwner__exact=localaccount.local_username)
            except ComputingActivity.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='ResourceID and LocalAccount not found')
        else:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Invalid request')
        serializer = ComputingActivity_Expand_Serializer(objects, many=True, context={'request': request})
        return MyAPIResponse({'result_set': serializer.data}, template_name='glue2_views_api/jobs.html')

class Jobs_by_ProfileID(APIView):
    '''
        GLUE2 Jobs from ComputingActivity
    '''
#    authentication_classes = (GlobusAuthentication,)
    permission_classes = (IsAuthenticated,)
    renderer_classes = (JSONRenderer,TemplateHTMLRenderer,)
    serializer_class = ComputingActivity_Expand_Serializer
    def get(self, request, format=None, **kwargs):
        fullusername = None
        username = None
        if request.user.is_authenticated:
            fullusername = request.user.username
            username = fullusername[:fullusername.rfind("@")]

            try:
                localaccounts = XSEDELocalUsermap.objects.filter(portal_login=username)
            except XSEDELocalUsermap.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='User not found in user database')
            localusernames = []
            resourceusers = {}
            for account in localaccounts:
                localuser = account.local_username
                localusernames.append(localuser)
                resourceusers[account.ResourceID+localuser] = True
            try:
                    objects = ComputingActivity.objects.filter(EntityJSON__LocalOwner__in=localusernames)
            except ComputingActivity.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='ResourceID and LocalAccount not found')
            jobstoreturn = []
            for job in objects:
                if resourceusers.get(job.ResourceID+job.EntityJSON['LocalOwner'], False):
                    jobstoreturn.append(job)
        else:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Invalid request')
        serializer = ComputingActivity_Expand_Serializer(jobstoreturn, many=True, context={'request': request})
        return MyAPIResponse({'result_set': serializer.data}, template_name='glue2_views_api/jobs.html')


class SearchGlobus(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = None

    def __init__(self, *args, **kwargs):
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
            if query_param[0] not in ['q', 'filter', 'fields', 'sort_by', 'limit', 'offset']:
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

    def post(self, request, *args, **kwargs):
        try:
            warehouse_software_model = DjangoWarehouseSoftware(**request.data)
            gmeta_list = {
                "ingest_type": "GMetaList",
                "ingest_data": {
                    "gmeta": [warehouse_software_model.model_dump()]
                }
            }
            self.search_client.ingest(self.search_endpoint, gmeta_list)
        except globus_sdk.SearchAPIError as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(gmeta_list, status.HTTP_200_OK)


@api_view(["GET"])
def compare_warehouse_view(request, *args, **kwargs):
    response = compare_warehouse()
    return Response(response, content_type="application/json")


@api_view(["GET", "POST",])
def ingest_globus_view(request, *args, **kwargs):
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

    globus_response = convert_to_globus(remote_response.json()["results"])

    return Response(
        globus_response,
        content_type="application/json",
        headers={"Accept": "application/json; indent=4"}
    )


def compare_warehouse():
    remote_response = requests.get(
        "https://operations-api.access-ci.org/wh2/resource/v4/local_search/",
        params={
            "affiliations": "access-ci.org",
        }
    )

    local_resources = ResourceV4Local.objects.filter(
        Affiliation__exact="access-ci.org"
    ).values()
    remote_resources = remote_response.json()["results"]

    results = compare_dicts(
        local_resources,
        remote_resources,
        group_by="ID",
        ignore_fields=[
            "CreationTime",
            "DetailURL",
            "EntityJSON.CreationTime",
            "Validity"
        ]
    )

    print(f"Added ({len(results['added'])}):")
    for item in results['added']:
        print(f"  {item}")

    print(f"\nRemoved ({len(results['removed'])}):")
    for item in results['removed']:
        print(f"  {item}")

    changes = []
    print(f"\nUpdated ({len(results['updated'])}):")
    for item in results['updated']:
        changes.append(item)
        print(f"  ID {item['ID']}:")
        print_changes(item['changes'], indent=4)

    response = [{
        "response": {
            "added": {
                "items": len(results['added']),
                "ID": [item["ID"] for item in results["added"]]
            },
            "removed": {
                "items": len(results["removed"]),
                "ID": [item["id"] for item in results["removed"]]
            },
            "updated": {
                "items": len(results["updated"]),
                "ID": [item["id"] for item in results["updated"]]
            }
        },
    }]

    return response


def compare_dicts(old_list, new_list, group_by=None, ignore_fields=None):
    """
    Compare two lists of dictionaries by their 'ID' key.

    Args:
        old_list: List of dictionaries from the old/database state
        new_list: List of dictionaries with the new state
        ignore_fields: Optional list of field names to ignore when comparing
                      Supports nested fields using dot notation (e.g., 'address.zip')

    Returns:
        dict with keys: 'added', 'removed', 'updated'
        - added: list of dicts that exist in new_list but not old_list
        - removed: list of dicts that exist in old_list but not new_list
        - updated: list of dicts where ID exists in both but values differ
    """
    if ignore_fields is None:
        ignore_fields = []

    # Always ignore ID field in change tracking
    ignore_fields = set(ignore_fields) | {'ID'}

    def should_ignore_field(field_path):
        """Check if a field path should be ignored."""
        return field_path in ignore_fields

    def compare_values(old_val, new_val, field_path=''):
        """
        Recursively compare values, handling nested dictionaries.
        Returns a dict of changes or None if no changes.
        """
        # Check if this field should be ignored
        if should_ignore_field(field_path):
            return None

        # Both are dicts - compare recursively
        if isinstance(old_val, dict) and isinstance(new_val, dict):
            all_keys = set(old_val.keys()) | set(new_val.keys())
            nested_changes = {}

            for key in all_keys:
                nested_path = f"{field_path}.{key}" if field_path else key

                if should_ignore_field(nested_path):
                    continue

                old_nested = old_val.get(key)
                new_nested = new_val.get(key)

                if old_nested != new_nested:
                    change = compare_values(old_nested, new_nested, nested_path)
                    if change:
                        nested_changes[key] = change

            return nested_changes if nested_changes else None

        # One or both are not dicts - direct comparison
        if old_val != new_val:
            change = {
                'old': old_val,
                'new': new_val
            }

            # Track if field was added or deleted
            if old_val is None:
                change['status'] = 'added'
            elif new_val is None:
                change['status'] = 'deleted'
            else:
                change['status'] = 'modified'

            return change

        return None
    # Convert lists to dicts keyed by "group_by" for O(1) lookup
    old_dict = {item[group_by]: item for item in old_list}
    new_dict = {item[group_by]: item for item in new_list}

    # Get ID sets for comparison
    old_ids = set(old_dict.keys())
    new_ids = set(new_dict.keys())

    # Find added, removed, and potentially updated IDs
    added_ids = new_ids - old_ids
    removed_ids = old_ids - new_ids
    common_ids = old_ids & new_ids

    # Collect results
    added = [new_dict[id] for id in added_ids]
    removed = [old_dict[id] for id in removed_ids]

    # For updated items, track what changed
    updated = []
    for id in common_ids:
        old_item = old_dict[id]
        new_item = new_dict[id]

        if old_item != new_item:
            changes = compare_values(old_item, new_item)

            if changes:
                # Remove the ID from changes if it exists
                changes.pop('ID', None)

                updated.append({
                    'ID': id,
                    'data': new_item,
                    'changes': changes
                })

    return {
        'added': added,
        'removed': removed,
        'updated': updated
    }


def convert_to_globus(response):
    from pprint import pprint

    globus_response = []
    for item in response:
        globus = {
            "Category": None,
            "CreationTime": item.get("CreationTime", None),
            "Default": False,
            "Description": item["EntityJSON"].get("Description", None),
            "HandleKey": item["EntityJSON"].get("HandleKey", None),
            "HandleType": item["EntityJSON"].get("HandleType", None),
            "ID": item.get("ID", None),
            "Info_GroupID": [group.get("info_groupid", []) 
                             for group in item["EntityJSON"].get("groups", [])],
            "Info_GroupName": [group.get("name", []) 
                               for group in item["EntityJSON"].get("groups", [])],
            "Info_ResourceID": item["EntityJSON"].get("info_resourceid", None),
            "Info_ResourceName": item["EntityJSON"].get("info_resourcename", None),
            "Keywords": [],
            "Name": None,
            "Organization_ID": [organization.get("organization_id", [])
                                for organization in item["EntityJSON"].get("organizations", [])],
            "Organization_Name": [organization.get("organization_name", []) 
                                  for organization in item["EntityJSON"].get("organizations", [])],
            "SupportContact": None,
            "SupportStatus": None,
            "URL": item["EntityJSON"].get("public_url", None),
            "Validity": item.get("Validity", None),
            "Version": None,
        }
        globus_response.append(globus)
        pprint(globus, indent=2)
    return globus_response


def print_changes(changes, indent=2):
    """Recursively print changes, handling nested dictionaries."""
    spacing = ' ' * indent

    for field, change in changes.items():
        # Check if this is a nested dictionary of changes
        if isinstance(change, dict) and 'old' not in change and 'new' not in change:
            print(f"{spacing}{field}:")
            print_changes(change, indent + 2)
        else:
            status = change.get('status', 'modified')
            if status == 'added':
                print(f"{spacing}{field}: [ADDED] → {change['new']}")
            elif status == 'deleted':
                print(f"{spacing}{field}: {change['old']} → [DELETED]")
            else:
                print(f"{spacing}{field}: {change['old']} → {change['new']}")
