from django.urls import path
from .views import *

urlpatterns = [
    path(r'v1/process/doctype/<str:doctype>/resourceid/<str:resourceid>/', glue2_process_doc.as_view(), name='glue2-process-doc'),

# Simple model routes

#    path(r'v1/admindomain/', AdminDomain_DbList.as_view(), name='admindomain-dblist'),
#    path(r'v1/admindomain/ID/(?P<pk>[^/]+)/', AdminDomain_DbDetail.as_view(), name='admindomain-detail'),
#
#    path(r'v1/userdomain/', UserDomain_DbList.as_view(), name='userdomain-dblist'),
#    path(r'v1/userdomain/ID/(?P<pk>[^/]+)/', UserDomain_DbDetail.as_view(), name='userdomain-detail'),
#
#    path(r'v1/accesspolicy/', AccessPolicy_DbList.as_view(), name='accesspolicy-dblist'),
#    path(r'v1/accesspolicy/ID/(?P<pk>[^/]+)/', AccessPolicy_DbDetail.as_view(), name='accesspolicy-detail'),
#
#    path(r'v1/contact/', Contact_DbList.as_view(), name='contact-dblist'),
#    path(r'v1/contact/ID/(?P<pk>[^/]+)/', Contact_DbDetail.as_view(), name='contact-detail'),
#
#    path(r'v1/location/', Location_DbList.as_view(), name='location-dblist'),
#    path(r'v1/location/ID/(?P<pk>[^/]+)/', Location_DbDetail.as_view(), name='location-detail'),
#
#    path(r'v1/applicationenvironment/', ApplicationEnvironment_DbList.as_view(), name='applicationenvironment-dblist'),
#    path(r'v1/applicationenvironment/ID/(?P<pk>[^/]+)/', ApplicationEnvironment_DbDetail.as_view(), name='applicationenvironment-detail'),
#
#    path(r'v1/applicationhandle/', ApplicationHandle_DbList.as_view(), name='applicationhandle-dblist'),
#    path(r'v1/applicationhandle/ID/(?P<pk>[^/]+)/', ApplicationHandle_DbDetail.as_view(), name='applicationhandle-detail'),
#
#    path(r'v1/abstractservice/', AbstractService_DbList.as_view(), name='abstractservice-dblist'),
#    path(r'v1/abstractservice/ID/(?P<pk>[^/]+)/', AbstractService_DbDetail.as_view(), name='abstractservice-detail'),
#
#    path(r'v1/endpoint/', Endpoint_DbList.as_view(), name='abstractservice-dblist'),
#    path(r'v1/endpoint/ID/(?P<pk>[^/]+)/', Endpoint_DbDetail.as_view(), name='endpoint-detail'),
#
    path(r'v1/computingmanager/', ComputingManager_DbList.as_view(), name='computingmanager-dblist'),
    path(r'v1/computingmanager/ID/<str:pk>/', ComputingManager_DbDetail.as_view(), name='computingmanager-detail'),

    path(r'v1/computingshare/', ComputingShare_DbList.as_view(), name='computingshare-dblist'),
    path(r'v1/computingshare/ID/<str:pk>/', ComputingShare_DbDetail.as_view(), name='computingshare-detail'),

    path(r'v1/executionenvironment/', ExecutionEnvironment_DbList.as_view(), name='executionenvironment-dblist'),
    path(r'v1/executionenvironment/ID/<str:pk>/', ExecutionEnvironment_DbDetail.as_view(), name='executionenvironment-detail'),

    path(r'v1/computingqueue/', ComputingQueue_DbList.as_view(), name='computingqueue-dblist'),
    path(r'v1/computingqueue/ResourceID/<str:resourceid>/', ComputingQueue_DbList.as_view(), name='computingqueue-dblist'),
    path(r'v1/computingqueue/ID/<str:pk>/', ComputingQueue_DbDetail.as_view(), name='computingqueue-detail'),
#
#    path(r'v1/computingactivity/', ComputingActivity_DbList.as_view(), name='computingactivity-dblist'),
#    path(r'v1/computingactivity/ID/(?P<pk>[^/]+)/', ComputingActivity_DbDetail.as_view(), name='computingactivity-detail'),
#
    path(r'v1/computingmanageracceleratorinfo/', ComputingManagerAcceleratorInfo_DbList.as_view(), name='computingmanageracceleratorinfo-dblist'),
    path(r'v1/computingmanageracceleratorinfo/ID/<str:pk>/', ComputingManagerAcceleratorInfo_DbDetail.as_view(), name='computingmanageracceleratorinfo-detail'),

    path(r'v1/computingshareacceleratorinfo/', ComputingShareAcceleratorInfo_DbList.as_view(), name='computingshareacceleratorinfo-dblist'),
    path(r'v1/computingshareacceleratorinfo/ID/<str:pk>/', ComputingShareAcceleratorInfo_DbDetail.as_view(), name='computingshareacceleratorinfo-detail'),

    path(r'v1/acceleratorenvironment/', AcceleratorEnvironment_DbList.as_view(), name='acceleratorenvironment-dblist'),
    path(r'v1/acceleratorenvironment/ID/<str:pk>/', AcceleratorEnvironment_DbDetail.as_view(), name='acceleratorenvironment-detail'),

    path(r'v1/entityhistory/ID/<str:id>/', EntityHistory_DbDetail.as_view(), name='entityhistory-detail'),

# Complex model routes
    path(r'v1/software/', Software_List.as_view(), name='software-list'),
    path(r'v1/software/ID/<path:id>/', Software_Detail.as_view(), name='software-detail'),
    path(r'v1/software/ResourceID/<str:resourceid>/', Software_Detail.as_view(), name='software-detail-onresource'),
    path(r'v1/software/AppName/<str:appname>/', Software_Detail.as_view(), name='software-detail'),

    path(r'v1/software_full/', Software_Full.as_view(), name='software-fulllist'),
    path(r'v1/software_full/ID/<path:id>/', Software_Full.as_view(), name='software-fulldetail'),
    path(r'v1/software_full/ResourceID/<str:resourceid>/', Software_Full.as_view(), name='software-fulldetail-onresource'),
    path(r'v1/software_full/AppName/<str:appname>/', Software_Full.as_view(), name='software-fulldetail-byname'),

    path(r'v1/software_fast/', Software_Fast.as_view(), name='software-fastlist'),

    path(r'v1/services/', Services_List.as_view(), name='services-list'),
    path(r'v1/services/ID/<str:id>/', Services_Detail.as_view(), name='services-detail'),
    path(r'v1/services/ResourceID/<str:resourceid>/', Services_Detail.as_view(), name='services-detail'),
    path(r'v1/services/InterfaceName/<str:interfacename>/', Services_Detail.as_view(), name='services-detail'),
    path(r'v1/services/ServiceType/<str:servicetype>/', Services_Detail.as_view(), name='services-detail'),

    path(r'v1/jobqueue/', Jobqueue_List.as_view(), name='jobsqueue-list'),
    path(r'v1/jobqueue/ResourceID/<str:resourceid>/', Jobqueue_List.as_view(), name='jobsqueue-list'),
    path(r'v1/jobs/', Jobqueue_List.as_view(), name='jobsqueue-list'),
    path(r'v1/jobs/ResourceID/<str:resourceid>/', Jobqueue_List.as_view(), name='jobsqueue-list'),
    path(r'v1/jobs2/ID/<str:id>/', Job_Detail.as_view(), name='jobs-detail'),
    path(r'v1/jobs2/ResourceID/<str:resourceid>/', Job_List.as_view(), name='jobs-list'),
    path(r'v1/userjobs/ResourceID/<str:resourceid>/', Jobs_per_Resource_by_ProfileID.as_view(), name='jobs-profileid'),
    path(r'v1/userjobs/', Jobs_by_ProfileID.as_view(), name='jobs-profileid'),
    path(r'v1/jobs2/ResourceID/<str:resourceid>/Queue/<str:queue>/', Job_List.as_view(), name='jobs-list'),
    path(r'v1/jobs2/ResourceID/<str:resourceid>/LocalAccount/<str:localaccount>/', Job_List.as_view(), name='jobs-list'),

]
