import traceback
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from django.db import transaction
from django.utils import timezone
from django.http import HttpResponse
from django.conf import settings
from django.db.models import Q

from integration_badges.models import *
from integration_badges.serializers import *
from cider.serializers import *

from warehouse_tools.exceptions import MyAPIException
from warehouse_tools.responses import MyAPIResponse

from drf_spectacular.utils import extend_schema, OpenApiParameter
import logging
from .permissions import IsRoadmapMaintainer, IsCoordinator, IsImplementer, ReadOnly

log = logging.getLogger(__name__)

badging_types = ('Compute', 'Storage')  # Expand as more roadmaps with badges are rolled out
badging_statuses = ('coming soon', 'friendly', 'pre-production', 'production', 'post-production')
badging_filter = Q(cider_type__in=badging_types) & Q(latest_status__in=badging_statuses) & Q(
    project_affiliation__icontains='ACCESS')

if hasattr(settings, 'DISABLE_PERMISSIONS_FOR_DEBUGGING'):
    if settings.DISABLE_PERMISSIONS_FOR_DEBUGGING == "True":
        DISABLE_PERMISSIONS_FOR_DEBUGGING = True
    else:
        DISABLE_PERMISSIONS_FOR_DEBUGGING = False
    #DISABLE_PERMISSIONS_FOR_DEBUGGING = settings.DISABLE_PERMISSIONS_FOR_DEBUGGING
else:
    DISABLE_PERMISSIONS_FOR_DEBUGGING = False


# _Detail_ includes all fields from a Model
# _Full_ includes fields from a model and dependent Models (i.e. roadmap badges, badge tasks, ..)
# _Min_ serializers include minimum set of fields

class Roadmap_Full_v1(GenericAPIView):
    '''
    Integration Roadmap(s) and related Badge details View
    '''
    permission_classes = (ReadOnly,)
    authentication_classes = []
    renderer_classes = (JSONRenderer,)
    serializer_class = Roadmap_Full_Serializer

    def get(self, request, format=None, **kwargs):
        roadmap_id = self.kwargs.get('roadmap_id')
        if roadmap_id:
            try:
                items = Roadmap.objects.get(pk=roadmap_id)
                many = False
            except Roadmap.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified roadmap_id not found')
        else:
            items = Roadmap.objects.all()
            many = True

        serializer = self.serializer_class(items, context={'request': request}, many=many)
        return MyAPIResponse({'results': serializer.data})


class Badge_Full_v1(GenericAPIView):
    '''
    Integration Badge(s) and pre-requisites
    '''
    permission_classes = (ReadOnly,)
    authentication_classes = []
    renderer_classes = (JSONRenderer,)
    serializer_class = Badge_Full_Serializer

    def get(self, request, format=None, **kwargs):
        badge_id = self.kwargs.get('badge_id')
        if badge_id:
            try:
                item = Badge.objects.get(pk=badge_id)
                many = False
            except Badge.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified badge_id not found')
        else:
            item = Badge.objects.all()
            many = True

        serializer = self.serializer_class(item, context={'request': request}, many=many)
        return MyAPIResponse({'results': serializer.data})


class Roadmap_Review_v1(GenericAPIView):
    '''
    Integration Roadmap Review Details
    '''
    permission_classes = (ReadOnly,)
    authentication_classes = []
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)
    serializer_class = Roadmap_Review_Serializer

    @extend_schema(operation_id='get_roadmap_review')
    def get(self, request, format=None, **kwargs):
        roadmaps_nav = Roadmap_Review_Nav_Serializer(Roadmap.objects.all(), context={'request': request},
                                                     many=True).data
        roadmap_id = self.kwargs.get('roadmap_id', roadmaps_nav[0]['roadmap_id'])
        roadmap = Roadmap.objects.get(pk=roadmap_id)
        serializer = self.serializer_class(roadmap, context={'request': request})
        results = {'roadmaps_nav': roadmaps_nav,
                   'roadmap': serializer.data}
        if request.accepted_renderer.format == 'html':
            return MyAPIResponse({'results': results}, template_name='integration_badges/roadmap_rp_information.html')
        else:
            return MyAPIResponse({'results': results})


class Badge_Review_v1(GenericAPIView):
    '''
    Badge Review Details
    '''
    permission_classes = (ReadOnly,)
    authentication_classes = []
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)
    serializer_class = Badge_Review_Serializer

    @extend_schema(
        operation_id='get_badge_review',
        parameters=[
            OpenApiParameter(
                name='mode',
                description='View mode',
                type=str,
                required=False,
                location=OpenApiParameter.PATH,
                enum=['badges', 'badgeresources'],
                #                , 'resourcebadges'],
                default='badges'
            )
        ]
    )
    def get(self, request, format=None, **kwargs):
        mode = request.query_params.get('mode', 'badges')
        roadmap_ids = set(i.roadmap_id for i in Roadmap.objects.filter(status='Production'))
        roadmap_badge_ids = set(i.badge_id for i in Roadmap_Badge.objects.filter(roadmap_id__in=roadmap_ids))
        badges = Badge.objects.filter(badge_id__in=roadmap_badge_ids).order_by('name')
        if mode in ('badgeresources'):
            serializer = Badge_Review_Extended_Serializer(badges, context={'request': request}, many=True)
        else:
            serializer = self.serializer_class(badges, context={'request': request}, many=True)
        results = {'mode': mode, 'badges': serializer.data}
        if mode in ('badgeresources'):
            results['roadmap_ids'] = roadmap_ids

        if request.accepted_renderer.format == 'html':
            return MyAPIResponse({'results': results}, template_name='integration_badges/badge_user_information.html')
        else:
            return MyAPIResponse({'results': results})


class Badge_Verification_v1(GenericAPIView):
    '''
    Badge Verification Status
    '''
    permission_classes = (ReadOnly,)
    authentication_classes = []
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)
    serializer_class = Resource_Badge_Verification_Serializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='status',
                description='Badge status',
                type=str,
                required=False,
                location=OpenApiParameter.PATH,
                enum=BadgeWorkflowStatus,
                default='task-completed'
            )
        ]
    )
    def get(self, request, format=None, **kwargs):
        mode = request.query_params.get('mode')
        roadmap_ids = set( i.roadmap_id for i in Roadmap.objects.filter(status='Production') )

        resource_badge_status = Resource_Badge_Workflow.objects.filter(roadmap_id__in=roadmap_ids).order_by('-status_updated_at')
        workflow_status = {}        # The latest resource badge status in selected roadmaps
        for item in resource_badge_status:
            key = f'{item.info_resourceid}:{item.roadmap_id}:{item.badge_id}'
            if key not in workflow_status:
                workflow_status[key] = {
                    'status_updated_by': item.status_updated_by,
                    'status_updated_at': item.status_updated_at,
                    'status': item.status,
                    'comment': item.comment }

        status_facet = {}
        unverified_badges = [] # All the ones that aren't in available/verified status
        resource_badges = Resource_Badge.objects.filter(roadmap_id__in=roadmap_ids).order_by('info_resourceid', 'badge__name')
        for badge in resource_badges:
            key = f'{badge.info_resourceid}:{badge.roadmap_id}:{badge.badge_id}'
            status = workflow_status.get(key, {'status': 'unknown'})    # Badge has no workflow entry
            facet_key = status.get('status').replace('-', '_')
            status_facet[facet_key] = status_facet[facet_key]+1 if facet_key in status_facet else 1
            if status.get('status') == 'verified':
                continue    # We're not returning or displaying this normal status
            data = self.serializer_class(badge).data
            data['workflow_status'] = status
            unverified_badges.append(data)
 
        if not mode:
            for x in ('task-completed', 'verification-failed', 'unknown', 'planned', 'deprecated'):
                facet_key = x.replace('-', '_')
                if status_facet.get(facet_key, 0) > 0:
                    mode = x
                    break
            mode = mode or 'task-completed'
                
        results = { 'mode': mode, 'status_facet': status_facet, 'resourcebadges': unverified_badges }
        
        if request.accepted_renderer.format == 'html':
            return MyAPIResponse({'results': results}, template_name='integration_badges/badge_verification_status.html')
        else:
            return MyAPIResponse({'results': results})


class Badge_Task_Full_v1(GenericAPIView):
    '''
    Retrieve an Integration Task by ID
    '''
    permission_classes = (ReadOnly,)
    authentication_classes = []
    renderer_classes = (JSONRenderer,)
    serializer_class = Badge_Task_Full_Serializer

    def get(self, request, *args, **kwargs):
        badge_id = kwargs.get('badge_id')
        if not badge_id:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Badge ID is required')

        badge_tasks = Badge_Task.objects.filter(badge_id=badge_id).order_by('sequence_no')
        if badge_tasks.exists():
            serializer = self.serializer_class(badge_tasks, context={'request': request}, many=True)
            return MyAPIResponse({'results': serializer.data})
        else:
            # Return empty list if no tasks found, not an error
            return MyAPIResponse({'results': []})


class Resources_Eligible_List_v1(GenericAPIView):
    '''
    Integration eligible CiDeR resources, which could be, are, or were integrated, but haven't been retired
    
    Based only on CiDeR since they may not have enrolled in a roadmap yet
    '''
    permission_classes = (ReadOnly,)
    authentication_classes = []
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderInfrastructure_Summary_Serializer

    @extend_schema(
        responses=CiderInfrastructure_Summary_Serializer,
    )
    def get(self, request, format=None, **kwargs):
        badging_statuses = ('coming soon', 'friendly', 'pre-production', 'production', 'post-production')
        # Will expand once more roadmaps with badges are rolled out
        badging_types = ('Compute', 'Storage')

        resources = CiderInfrastructure.objects.filter(badging_filter)
        serializer = self.serializer_class(resources, context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})


class Resource_Full_v1(GenericAPIView):
    '''
    Resource full details, including roadmaps, badges, and badge status
    '''
    if DISABLE_PERMISSIONS_FOR_DEBUGGING:
        permission_classes = (AllowAny,)
    else:
        # permission_classes = [IsCoordinator | (IsAuthenticated & ReadOnly)]
        permission_classes = (ReadOnly,)
        authentication_classes = []

    renderer_classes = (JSONRenderer,)
    serializer_class = Resource_Full_Serializer

    def get(self, request, format=None, **kwargs):
        info_resourceid = kwargs.get('info_resourceid')
        if not info_resourceid:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Info_ResourceID is required')

        try:
            resource = CiderInfrastructure.objects.get(Q(info_resourceid=info_resourceid) & badging_filter)
        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND,
                                 detail='Specified Info_ResourceID does not exist or is not eligible')

        serializer = self.serializer_class(resource, context={'request': request}, many=False)
        return MyAPIResponse({'results': serializer.data})


class Resource_Roadmap_Enrollments_v1(GenericAPIView):
    '''
    Resource roadmap and roadmap badge enrollments
    '''
    if DISABLE_PERMISSIONS_FOR_DEBUGGING:
        permission_classes = (AllowAny,)
    else:
        permission_classes = [IsCoordinator | (IsAuthenticated & ReadOnly)]

    renderer_classes = (JSONRenderer,)
    serializer_class = Resource_Enrollments_Serializer

    @extend_schema(
        responses=Resource_Enrollments_Response_Serializer,
    )
    def post(self, request, format=None, **kwargs):
        info_resourceid = kwargs.get('info_resourceid')
        if not info_resourceid:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='Info_ResourceID is required')
        roadmap_id = kwargs.get('roadmap_id')
        if not roadmap_id:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='RoadmapID is required')
        try:
            resource = CiderInfrastructure.objects.get(Q(info_resourceid=info_resourceid) & badging_filter)
            roadmap = Roadmap.objects.get(pk=roadmap_id)
        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND,
                                 detail='Specified Info_ResourceID does not exist or is not eligible')
        except Roadmap.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified RoadmapID not found')

        message = ''
        enroll_badges = []
        unenroll_badges = []

        # Enroll Resource in Roadmap if not already enrolled
        try:
            resource_roadmap = Resource_Roadmap.objects.get(info_resourceid=info_resourceid, roadmap=roadmap)
        except Resource_Roadmap.DoesNotExist:
            resource_roadmap = None
        except Exception as exc:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='{}: {}'.format(type(exc).__name__, exc))
        if not resource_roadmap:
            try:
                resource_roadmap = Resource_Roadmap(info_resourceid=info_resourceid, roadmap=roadmap).save()
                message += f'Enrolled roadmap={roadmap.name}'
            except Exception as exc:
                raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='{}: {}'.format(type(exc).__name__, exc))

        # Check that badge_ids were specified
        raw_badge_ids = request.data.get('badge_ids')
        if not raw_badge_ids or type(raw_badge_ids) is not list:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Missing BadgeIDs or not a list')
        new_badge_ids = list(str(id) for id in raw_badge_ids)

        # Verify that each badge is available in the roadmap
        for id in new_badge_ids:
            try:
                new_roadmap_badge = Roadmap_Badge.objects.get(roadmap_id=roadmap_id, badge_id=id)
            except Roadmap_Badge.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND,
                                     detail=f'Badge.ID ({id}) is not availabe in roadmap ({roadmap_id})')

        # Retrieve current badges
        try:
            cur_badges = Resource_Badge.objects.filter(info_resourceid=info_resourceid, roadmap_id=roadmap_id)
            cur_badge_ids = [str(id) for id in cur_badges.values_list('badge_id', flat=True)]
        except Exception as exc:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='{}: {}'.format(type(exc).__name__, exc))

        # Check and enroll in badges
        for id in new_badge_ids:
            if id not in cur_badge_ids:
                try:
                    Resource_Badge(info_resourceid=info_resourceid, roadmap_id=roadmap_id, badge_id=id).save(
                        username=get_current_username(request.user))
                except Exception as exc:
                    raise MyAPIException(code=status.HTTP_400_BAD_REQUEST,
                                         detail='{}: {}'.format(type(exc).__name__, exc))
                enroll_badges.append(id)

        # Check and unenroll in badges
        for cur in cur_badges:
            if str(cur.badge_id) not in new_badge_ids:
                try:
                    cur.delete()
                except Exception as exc:
                    raise MyAPIException(code=status.HTTP_400_BAD_REQUEST,
                                         detail='{}: {}'.format(type(exc).__name__, exc))
                unenroll_badges.append(str(cur.badge_id))

        if enroll_badges:
            message += '; ' if message else ''
            message += f'Enrolled badges=({",".join(enroll_badges)})'
        if unenroll_badges:
            message += '; ' if message else ''
            message += f'Unenrolled badges=({",".join(unenroll_badges)})'
        return MyAPIResponse({'message': message})


class Resource_Badge_Status_v1(GenericAPIView):
    '''
    Record Badge Status
    '''
    if DISABLE_PERMISSIONS_FOR_DEBUGGING:
        permission_classes = (AllowAny,)
    else:
        permission_classes = [IsCoordinator | (IsAuthenticated & ReadOnly)]

    renderer_classes = (JSONRenderer,)
    serializer_class = Resource_Workflow_Post_Serializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='badge_workflow_status',
                description='Workflow status',
                type=str,
                required=True,
                location=OpenApiParameter.PATH,
                enum=BadgeWorkflowStatus,
                default=BadgeWorkflowStatus.PLANNED
            )
        ],
        request=Resource_Workflow_Post_Serializer,
    )
    def post(self, request, badge_workflow_status, *args, **kwargs):
        info_resourceid = kwargs.get('info_resourceid')
        roadmap_id = kwargs.get('roadmap_id')
        badge_id = kwargs.get('badge_id')
        if not info_resourceid or not roadmap_id or not badge_id or not badge_workflow_status:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST,
                                 detail='Info_ResourceID, Roadmap ID, Badge ID and status are required')

        try:
            resource = CiderInfrastructure.objects.get(info_resourceid=info_resourceid)
            roadmap = Roadmap.objects.get(pk=roadmap_id)
            badge = Badge.objects.get(pk=badge_id)
            resource_badge = Resource_Badge.objects.get(info_resourceid=info_resourceid, roadmap=roadmap, badge=badge)
        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified resource not found')
        except Roadmap.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified roadmap not found')
        except Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified badge not found')
        except Resource_Badge.DoesNotExist:
            resource_badge = Resource_Badge(
                info_resourceid=info_resourceid,
                roadmap=roadmap,
                badge=badge
            )
            resource_badge.save(username=get_current_username(request.user))

        updated_by = request.data.get('status_updated_by')
        if not updated_by:
            updated_by = get_current_username(request.user)

        if badge_workflow_status is None:
            badge_workflow_status = resource_badge.status

        workflow = Resource_Badge_Workflow(
            info_resourceid=info_resourceid,
            roadmap=roadmap,
            badge=badge,
            status=badge_workflow_status,
            status_updated_by=updated_by,
            comment=request.data.get('comment')
        )
        workflow.save()

        return MyAPIResponse({
            'message': 'Badge marked as %s' % badge_workflow_status,
            'status_updated_at': workflow.status_updated_at
        })


class Resource_Badge_Task_Status_v1(GenericAPIView):
    '''
    Record Badge Task Status
    '''
    if DISABLE_PERMISSIONS_FOR_DEBUGGING:
        permission_classes = (AllowAny,)
    else:
        permission_classes = [IsCoordinator | (IsAuthenticated & ReadOnly)]

    renderer_classes = (JSONRenderer,)
    serializer_class = Resource_Workflow_Post_Serializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='badge_task_workflow_status',
                description='Filter by status',
                type=str,
                required=True,
                location=OpenApiParameter.PATH,
                enum=BadgeTaskWorkflowStatus,
                default=BadgeTaskWorkflowStatus.COMPLETED
            )
        ],
        request=Resource_Workflow_Post_Serializer,
    )
    def post(self, request, badge_task_workflow_status, *args, **kwargs):
        info_resourceid = kwargs.get('info_resourceid')
        roadmap_id = kwargs.get('roadmap_id')
        badge_id = kwargs.get('badge_id')
        task_id = kwargs.get('task_id')
        if not info_resourceid or not roadmap_id or not badge_id or not task_id or not badge_task_workflow_status:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST,
                                 detail='Info_ResourceID, Roadmap ID, Badge ID, Task ID and status are required')

        try:
            resource = CiderInfrastructure.objects.get(info_resourceid=info_resourceid)
            roadmap = Roadmap.objects.get(pk=roadmap_id)
            badge = Badge.objects.get(pk=badge_id)
            task = Task.objects.get(pk=task_id)
            resource_badge = Resource_Badge.objects.get(info_resourceid=info_resourceid, roadmap=roadmap, badge=badge)
            badge_task = Badge_Task.objects.get(badge=badge, task=task)
        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified resource not found')
        except Roadmap.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified roadmap not found')
        except Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified badge not found')
        except Task.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified task not found')
        except Resource_Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND,
                                 detail='Specified resource-badge relationship not found')
        except Badge_task.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified badge-task relationship not found')

        updated_by = request.data.get('status_updated_by')
        if not updated_by:
            updated_by = get_current_username(request.user)

        if resource_badge.status == BadgeWorkflowStatus.VERIFIED or resource_badge.status == BadgeWorkflowStatus.TASKS_COMPLETED:
            workflow = Resource_Badge_Workflow(
                info_resourceid=info_resourceid,
                roadmap=roadmap,
                badge=badge,
                status=BadgeWorkflowStatus.PLANNED,
                status_updated_by=updated_by,
                comment=f"Reopened by the task (taskId={task_id}) '{task.name}'"
            )
            workflow.save()

        workflow = Resource_Badge_Task_Workflow(
            info_resourceid=info_resourceid,
            roadmap=roadmap,
            badge=badge,
            task=task,
            status=badge_task_workflow_status,
            status_updated_by=updated_by,
            comment=request.data.get('comment')
        )
        workflow.save()

        return MyAPIResponse({
            'message': 'Badge task marked as %s' % badge_task_workflow_status,
            'status_updated_at': workflow.status_updated_at
        })


class Resource_Roadmap_Badge_Log_v1(GenericAPIView):
    '''
    Retrieve all or one resource badge(s) and their status
    '''
    if DISABLE_PERMISSIONS_FOR_DEBUGGING:
        permission_classes = (AllowAny,)
    else:
        # permission_classes = [IsCoordinator | (IsAuthenticated & ReadOnly)]
        permission_classes = (ReadOnly,)
        authentication_classes = []

    renderer_classes = (JSONRenderer,)
    serializer_class = Resource_Roadmap_Serializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='info_resourceid',
                description='Info ResourceID',
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='roadmap_id',
                description='Roadmap ID',
                type=str,
                required=False,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='badge_id',
                description='Badge ID',
                type=str,
                required=False,
                location=OpenApiParameter.QUERY
            )
        ]
    )
    def get(self, request, format=None, **kwargs):
        info_resourceid = self.request.query_params.get('info_resourceid')
        roadmap_id = self.request.query_params.get('roadmap_id')
        badge_id = self.request.query_params.get('badge_id')

        try:
            if info_resourceid is not None:
                resource = CiderInfrastructure.objects.get(info_resourceid=info_resourceid)

            if roadmap_id is not None:
                roadmap = Roadmap.objects.get(pk=roadmap_id)

            if info_resourceid is not None and roadmap_id is not None:
                resource_roadmap = Resource_Roadmap.objects.get(info_resourceid=info_resourceid, roadmap_id=roadmap_id)

            if badge_id is not None:
                badge = Badge.objects.get(pk=badge_id)

            if roadmap_id is not None and badge_id is not None:
                roadmap_badge = Roadmap_Badge.objects.get(roadmap_id=roadmap_id, badge_id=badge_id)

        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified Info_ResourceID not found')
        except Roadmap.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified RoadmapID not found')
        except Resource_Roadmap.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND,
                                 detail='Specified resource-roadmap relationship not found not found')
        except Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified BadgeID not found')
        except Roadmap_Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND,
                                 detail='Specified roadmap-badge relationship not found not found')

        badges_status = []

        resource_roadmaps = Resource_Roadmap.objects.all()
        if info_resourceid is not None:
            resource_roadmaps = resource_roadmaps.filter(info_resourceid=info_resourceid)
        if roadmap_id is not None:
            resource_roadmaps = resource_roadmaps.filter(roadmap_id=roadmap_id)

        for resource_roadmap in resource_roadmaps:
            roadmap_badges = Roadmap_Badge.objects.all().filter(roadmap_id=resource_roadmap.roadmap_id)
            if badge_id is not None:
                roadmap_badges = roadmap_badges.filter(badge_id=badge_id)

            for roadmap_badge in roadmap_badges:
                resource_badge_logs = Resource_Badge_Workflow.objects.all().filter(
                    info_resourceid=resource_roadmap.info_resourceid,
                    roadmap_id=resource_roadmap.roadmap_id,
                    badge_id=roadmap_badge.badge_id).order_by('-status_updated_at')

                for resource_badge_log in resource_badge_logs:
                    badge_status = {
                        'id': resource_badge_log.workflow_id,
                        'info_resourceid': resource_badge_log.info_resourceid,
                        'roadmap_id': resource_badge_log.roadmap_id,
                        'badge_id': resource_badge_log.badge_id,
                        'status': resource_badge_log.status,
                        'status_updated_by': resource_badge_log.status_updated_by,
                        'status_updated_at': resource_badge_log.status_updated_at,
                        'comment': resource_badge_log.comment
                    }
                    badges_status.append(badge_status)
        return MyAPIResponse({'results': badges_status})


class Resource_Roadmap_Badges_Status_v1(GenericAPIView):
    '''
    Retrieve all or one resource badge(s) and their status
    '''
    if DISABLE_PERMISSIONS_FOR_DEBUGGING:
        permission_classes = (AllowAny,)
    else:
        # permission_classes = [IsCoordinator | (IsAuthenticated & ReadOnly)]
        permission_classes = (ReadOnly,)
        authentication_classes = []

    renderer_classes = (JSONRenderer,)
    serializer_class = Resource_Roadmap_Serializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='info_resourceid',
                description='Info ResourceID',
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='roadmap_id',
                description='Roadmap ID',
                type=str,
                required=False,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='badge_id',
                description='Badge ID',
                type=str,
                required=False,
                location=OpenApiParameter.QUERY
            )
        ]
    )
    def get(self, request, format=None, **kwargs):
        info_resourceid = self.request.query_params.get('info_resourceid')
        roadmap_id = self.request.query_params.get('roadmap_id')
        badge_id = self.request.query_params.get('badge_id')

        try:
            if info_resourceid is not None:
                resource = CiderInfrastructure.objects.get(info_resourceid=info_resourceid)

            if roadmap_id is not None:
                roadmap = Roadmap.objects.get(pk=roadmap_id)

            if info_resourceid is not None and roadmap_id is not None:
                resource_roadmap = Resource_Roadmap.objects.get(info_resourceid=info_resourceid, roadmap_id=roadmap_id)

            if badge_id is not None:
                badge = Badge.objects.get(pk=badge_id)

            if roadmap_id is not None and badge_id is not None:
                roadmap_badge = Roadmap_Badge.objects.get(roadmap_id=roadmap_id, badge_id=badge_id)

        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified Info_ResourceID not found')
        except Roadmap.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified RoadmapID not found')
        except Resource_Roadmap.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND,
                                 detail='Specified resource-roadmap relationship not found not found')
        except Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified BadgeID not found')
        except Roadmap_Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND,
                                 detail='Specified roadmap-badge relationship not found not found')

        badges_status = []

        resource_roadmaps = Resource_Roadmap.objects.all()
        if info_resourceid is not None:
            resource_roadmaps = resource_roadmaps.filter(info_resourceid=info_resourceid)
        if roadmap_id is not None:
            resource_roadmaps = resource_roadmaps.filter(roadmap_id=roadmap_id)

        for resource_roadmap in resource_roadmaps:
            roadmap_badges = Roadmap_Badge.objects.all().filter(roadmap_id=resource_roadmap.roadmap_id)
            if badge_id is not None:
                roadmap_badges = roadmap_badges.filter(badge_id=badge_id)

            for roadmap_badge in roadmap_badges:
                resource_badges = Resource_Badge.objects.all().filter(info_resourceid=resource_roadmap.info_resourceid,
                                                                      roadmap_id=resource_roadmap.roadmap_id,
                                                                      badge_id=roadmap_badge.badge_id)

                for resource_badge in resource_badges:
                    badge_status = {
                        'id': resource_badge.id,
                        'info_resourceid': resource_badge.info_resourceid,
                        'roadmap_id': resource_badge.roadmap_id,
                        'badge_id': resource_badge.badge_id,
                        'badge_access_url': resource_badge.badge_access_url,
                        'badge_access_url_label': resource_badge.badge_access_url_label,
                        'status': resource_badge.status,
                        'status_updated_by': resource_badge.workflow.status_updated_by if resource_badge.workflow else None,
                        'status_updated_at': resource_badge.workflow.status_updated_at if resource_badge.workflow else None,
                        'comment': resource_badge.workflow.comment if resource_badge.workflow else None
                    }
                    badges_status.append(badge_status)
        return MyAPIResponse({'results': badges_status})


class Resource_Roadmap_Badge_Tasks_Status_v1(GenericAPIView):
    '''
    Retrieve details of a specific resource, including roadmaps and their badges.
    It also includes the list of badge statuses of the badges that are at least planned.
    '''
    if DISABLE_PERMISSIONS_FOR_DEBUGGING:
        permission_classes = (AllowAny,)
    else:
        # permission_classes = [IsCoordinator | (IsAuthenticated & ReadOnly)]
        permission_classes = (ReadOnly,)
        authentication_classes = []

    renderer_classes = (JSONRenderer,)
    serializer_class = Resource_Roadmap_Serializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='info_resourceid',
                description='Info ResourceID',
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='roadmap_id',
                description='Roadmap ID',
                type=str,
                required=False,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='badge_id',
                description='Badge ID',
                type=str,
                required=False,
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='task_id',
                description='Task ID',
                type=str,
                required=False,
                location=OpenApiParameter.QUERY
            )
        ]
    )
    def get(self, request, format=None, **kwargs):
        info_resourceid = self.request.query_params.get('info_resourceid')
        roadmap_id = self.request.query_params.get('roadmap_id')
        badge_id = self.request.query_params.get('badge_id')
        task_id = self.request.query_params.get('task_id')

        # if not info_resourceid or not roadmap_id or not badge_id:
        #     raise MyAPIException(code=status.HTTP_400_BAD_REQUEST,
        #                          detail='Info_ResourceID, RoadmapID and BadgeID are required')

        try:
            if info_resourceid is not None:
                resource = CiderInfrastructure.objects.get(info_resourceid=info_resourceid)

            if roadmap_id is not None:
                roadmap = Roadmap.objects.get(pk=roadmap_id)

            if info_resourceid is not None and roadmap_id is not None:
                resource_roadmap = Resource_Roadmap.objects.get(info_resourceid=info_resourceid, roadmap_id=roadmap_id)

            if badge_id is not None:
                badge = Badge.objects.get(pk=badge_id)

            if roadmap_id is not None and badge_id is not None:
                roadmap_badge = Roadmap_Badge.objects.get(roadmap_id=roadmap_id, badge_id=badge_id)

            if task_id is not None:
                task = Task.objects.get(pk=task_id)

            if badge_id is not None and task_id is not None:
                badge_task = Badge_Task.objects.get(badge_id=badge_id, task_id=task_id)

        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified Info_ResourceID not found')
        except Roadmap.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified RoadmapID not found')
        except Resource_Roadmap.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND,
                                 detail='Specified resource-roadmap relationship not found not found')
        except Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified BadgeID not found')
        except Roadmap_Badge.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND,
                                 detail='Specified roadmap-badge relationship not found not found')
        except Task.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='Specified TaskID not found')
        except Badge_Task.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND,
                                 detail='Specified badge-task relationship not found not found')

        task_status = []

        resource_roadmaps = Resource_Roadmap.objects.all()
        if info_resourceid is not None:
            resource_roadmaps = resource_roadmaps.filter(info_resourceid=info_resourceid)
        if roadmap_id is not None:
            resource_roadmaps = resource_roadmaps.filter(roadmap_id=roadmap_id)

        for resource_roadmap in resource_roadmaps:
            roadmap_badges = Roadmap_Badge.objects.all().filter(roadmap_id=resource_roadmap.roadmap_id)
            if badge_id is not None:
                roadmap_badges = roadmap_badges.filter(badge_id=badge_id)

            for roadmap_badge in roadmap_badges:
                resource_badges = Resource_Badge.objects.all().filter(info_resourceid=resource_roadmap.info_resourceid,
                                                                      roadmap_id=resource_roadmap.roadmap_id,
                                                                      badge_id=roadmap_badge.badge_id)
                if badge_id is not None:
                    resource_badges = resource_badges.filter(badge_id=roadmap_badge.badge_id)

                for resource_badge in resource_badges:
                    badge_tasks = Badge_Task.objects.all().filter(badge_id=resource_badge.badge_id)
                    if task_id is not None:
                        badge_tasks = badge_tasks.filter(task_id=task_id)

                    for badge_task in badge_tasks:
                        task_workflow = Resource_Badge_Task_Workflow.objects.filter(
                            info_resourceid=resource_roadmap.info_resourceid,
                            roadmap_id=resource_roadmap.roadmap_id,
                            badge_id=badge_task.badge_id,
                            task_id=badge_task.task_id
                        ).order_by('-status_updated_at').first()
                        if task_workflow is not None:
                            task_status.append({
                                "task_id": badge_task.task_id,
                                "task_name": badge_task.task.name,
                                "status": task_workflow.status,
                                "status_updated_by": task_workflow.status_updated_by,
                                "status_updated_at": task_workflow.status_updated_at
                            })
                        else:
                            task_status.append({
                                "task_id": badge_task.task_id,
                                "task_name": badge_task.task.name,
                                "status": None,
                                "status_updated_by": None,
                                "status_updated_at": None
                            })

        return MyAPIResponse({'results': task_status})


class DatabaseFile_v1(GenericAPIView):
    '''
    Retrieve tasks of a specific badge.
    '''
    permission_classes = (ReadOnly,)
    authentication_classes = []
    renderer_classes = (JSONRenderer,)
    serializer_class = DatabaseFile_Serializer

    def get(self, request, *args, **kwargs):
        file_id = kwargs.get('file_id')
        if not file_id:
            raise MyAPIException(code=status.HTTP_400_BAD_REQUEST, detail='File ID is required')

        try:
            file = DatabaseFile.objects.get(pk=file_id)
        except DatabaseFile.DoesNotExist:
            raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail='File not found')

        response = HttpResponse(file.file_data, content_type=file.content_type)
        response['Content-Disposition'] = 'inline; filename="%s"' % file.file_name

        return response
