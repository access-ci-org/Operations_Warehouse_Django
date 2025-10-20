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
from django.db.models import Subquery, OuterRef, Exists, Max, Count

from integration_badges.models import *
from integration_badges.serializers import *
from cider.serializers import *

from warehouse_tools.exceptions import MyAPIException
from warehouse_tools.responses import MyAPIResponse

from drf_spectacular.utils import extend_schema, OpenApiParameter
import logging

from .models import Resource_Badge_Workflow
from .permissions import IsRoadmapMaintainer, IsCoordinator, IsImplementer, IsConcierge, ReadOnly

log = logging.getLogger(__name__)

badging_types = (
    "Compute",
    "Storage",
    "Network",
    "Data",
)  # Expand as more roadmaps with badges are rolled out
badging_statuses = (
    "coming soon",
    "friendly",
    "pre-production",
    "production",
    "post-production",
)
badging_filter = (
    Q(cider_type__in=badging_types)
    & Q(latest_status__in=badging_statuses)
    & Q(project_affiliation__icontains="ACCESS")
)

if hasattr(settings, "DISABLE_PERMISSIONS_FOR_DEBUGGING"):
    if settings.DISABLE_PERMISSIONS_FOR_DEBUGGING == "True":
        DISABLE_PERMISSIONS_FOR_DEBUGGING = True
    else:
        DISABLE_PERMISSIONS_FOR_DEBUGGING = False
    # DISABLE_PERMISSIONS_FOR_DEBUGGING = settings.DISABLE_PERMISSIONS_FOR_DEBUGGING
else:
    DISABLE_PERMISSIONS_FOR_DEBUGGING = False


def get_group_id(info_resourceid):
    try:
        cidergroup = CiderGroups.objects.filter(
            info_resourceids__contains=[info_resourceid]
        ).first()
    except Exception:
        return False
    if not cidergroup:
        raise (ResourceIDError(f"{info_resourceid} not found in any CiderGroup"))
        return False
    else:
        return cidergroup.info_groupid


# _Detail_ includes all fields from a Model
# _Full_ includes fields from a model and dependent Models (i.e. roadmap badges, badge tasks, ..)
# _Min_ serializers include minimum set of fields


class Roadmap_Full_v1(GenericAPIView):
    """
    Integration Roadmap(s) and related Badge details View
    """

    if DISABLE_PERMISSIONS_FOR_DEBUGGING:
        permission_classes = (AllowAny,)
    else:
        permission_classes = [IsConcierge | (IsAuthenticated & ReadOnly)]

    renderer_classes = (JSONRenderer,)
    serializer_class = Roadmap_Full_Serializer

    def get(self, request, format=None, **kwargs):
        roadmap_id = self.kwargs.get("roadmap_id")
        if roadmap_id:
            try:
                items = Roadmap.objects.get(pk=roadmap_id)
                many = False
            except Roadmap.DoesNotExist:
                raise MyAPIException(
                    code=status.HTTP_404_NOT_FOUND,
                    detail="Specified roadmap_id not found",
                )
        else:
            items = Roadmap.objects.all()
            many = True

        serializer = self.serializer_class(
            items, context={"request": request}, many=many
        )
        return MyAPIResponse({"results": serializer.data})


    def post(self, request, format=None, **kwargs):
        roadmap_id = self.kwargs.get('roadmap_id')

        name = request.data.get('name')
        executive_summary = request.data.get('executive_summary')
        infrastructure_types = request.data.get('infrastructure_types')
        integration_coordinators = request.data.get('integration_coordinators')
        status = request.data.get('status')
        badges = request.data.get('badges')

        for badge in badges:
            try:
                Badge.objects.get(badge_id=badge.get('badge_id'))
            except Badge.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail=f'Badge not found ({badge.get("badge_id")})')

        if roadmap_id:
            try:
                roadmap = Roadmap.objects.get(roadmap_id=roadmap_id)
            except Roadmap.DoesNotExist:
                raise MyAPIException(code=status.HTTP_404_NOT_FOUND, detail=f'Roadmap not found ({roadmap_id})')

            roadmap.name = name
            roadmap.executive_summary = executive_summary
            roadmap.infrastructure_types = infrastructure_types
            roadmap.integration_coordinators = integration_coordinators
            roadmap.status = status

            roadmap.save()

            Roadmap_Badge.objects.filter(roadmap_id=roadmap_id).delete()
        else:
            roadmap = Roadmap(
                name=name,
                executive_summary=executive_summary,
                infrastructure_types=infrastructure_types,
                integration_coordinators=integration_coordinators,
                status=status
            )
            roadmap.save()

        for sequence_no in range(len(badges)):
            badge = badges[sequence_no]
            Roadmap_Badge(
                roadmap=roadmap,
                badge_id=badge.get('badge_id'),
                sequence_no=sequence_no,
                required=badge.get('required')
            ).save()


        serializer = self.serializer_class(roadmap, context={'request': request}, many=False)
        return MyAPIResponse({'results': serializer.data})


class Badge_Full_v1(GenericAPIView):
    """
    Integration Badge(s) and pre-requisites
    """

    permission_classes = (ReadOnly,)
    authentication_classes = []
    renderer_classes = (JSONRenderer,)
    serializer_class = Badge_Full_Serializer

    def get(self, request, format=None, **kwargs):
        badge_id = self.kwargs.get("badge_id")
        if badge_id:
            try:
                item = Badge.objects.get(pk=badge_id)
                many = False
            except Badge.DoesNotExist:
                raise MyAPIException(
                    code=status.HTTP_404_NOT_FOUND,
                    detail="Specified badge_id not found",
                )
        else:
            item = Badge.objects.all()
            many = True

        serializer = self.serializer_class(
            item, context={"request": request}, many=many
        )
        return MyAPIResponse({"results": serializer.data})


class Roadmap_Review_v1(GenericAPIView):
    """
    Integration Roadmap Review Details
    """

    permission_classes = (ReadOnly,)
    authentication_classes = []
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)
    serializer_class = Roadmap_Review_Serializer

    @extend_schema(operation_id="get_roadmap_review")
    def get(self, request, format=None, **kwargs):
        roadmaps_nav = Roadmap_Review_Nav_Serializer(
            Roadmap.objects.all(), context={"request": request}, many=True
        ).data
        roadmap_id = self.kwargs.get("roadmap_id", roadmaps_nav[0]["roadmap_id"])
        roadmap = Roadmap.objects.get(pk=roadmap_id)
        serializer = self.serializer_class(roadmap, context={"request": request})
        results = {"roadmaps_nav": roadmaps_nav, "roadmap": serializer.data}
        if request.accepted_renderer.format == "html":
            return MyAPIResponse(
                {"results": results},
                template_name="integration_badges/roadmap_rp_information.html",
            )
        else:
            return MyAPIResponse({"results": results})


class Badge_Review_v1(GenericAPIView):
    """
    Badge Review Details
    """

    permission_classes = (ReadOnly,)
    authentication_classes = []
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)
    serializer_class = Badge_Review_Serializer

    @extend_schema(
        operation_id="get_badge_review",
        parameters=[
            OpenApiParameter(
                name="mode",
                description="View mode",
                type=str,
                required=False,
                location=OpenApiParameter.PATH,
                enum=["badges", "badgeresources"],
                #                , 'resourcebadges'],
                default="badges",
            )
        ],
    )
    def get(self, request, format=None, **kwargs):
        mode = request.query_params.get("mode", "badges")
        roadmap_ids = set(
            i.roadmap_id for i in Roadmap.objects.filter(status="Production")
        )
        roadmap_badge_ids = set(
            i.badge_id for i in Roadmap_Badge.objects.filter(roadmap_id__in=roadmap_ids)
        )
        badges = Badge.objects.filter(badge_id__in=roadmap_badge_ids).order_by("name")
        if mode in ("badgeresources"):
            serializer = Badge_Review_Extended_Serializer(
                badges, context={"request": request}, many=True
            )
        else:
            serializer = self.serializer_class(
                badges, context={"request": request}, many=True
            )
        results = {"mode": mode, "badges": serializer.data}
        if mode in ("badgeresources"):
            results["roadmap_ids"] = roadmap_ids

        if request.accepted_renderer.format == "html":
            return MyAPIResponse(
                {"results": results},
                template_name="integration_badges/badge_user_information.html",
            )
        else:
            return MyAPIResponse({"results": results})


class Badge_Verification_v1(GenericAPIView):
    """
    Badge Verification Status
    """

    permission_classes = (ReadOnly,)
    authentication_classes = []
    renderer_classes = (JSONRenderer, TemplateHTMLRenderer)
    serializer_class = Resource_Badge_Verification_Serializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="status",
                description="Badge status",
                type=str,
                required=False,
                location=OpenApiParameter.PATH,
                enum=BadgeWorkflowStatus,
                default="task-completed",
            )
        ]
    )
    def get(self, request, format=None, **kwargs):
        mode = request.query_params.get("mode")
        roadmap_ids = set(
            i.roadmap_id for i in Roadmap.objects.filter(status="Production")
        )

        resource_badge_status = Resource_Badge_Workflow.objects.filter(
            roadmap_id__in=roadmap_ids
        ).order_by("-status_updated_at")
        workflow_status = {}  # The latest resource badge status in selected roadmaps
        for item in resource_badge_status:
            key = f"{item.info_resourceid}:{item.roadmap_id}:{item.badge_id}"
            if key not in workflow_status:
                workflow_status[key] = {
                    "status_updated_by": item.status_updated_by,
                    "status_updated_at": item.status_updated_at,
                    "status": item.status,
                    "comment": item.comment,
                }

        status_facet = {}
        unverified_badges = []  # All the ones that aren't in available/verified status
        resource_badges = Resource_Badge.objects.filter(
            roadmap_id__in=roadmap_ids
        ).order_by("info_resourceid", "badge__name")
        for badge in resource_badges:
            key = f"{badge.info_resourceid}:{badge.roadmap_id}:{badge.badge_id}"
            status = workflow_status.get(
                key, {"status": "unknown"}
            )  # Badge has no workflow entry
            facet_key = status.get("status").replace("-", "_")
            status_facet[facet_key] = (
                status_facet[facet_key] + 1 if facet_key in status_facet else 1
            )
            if status.get("status") == "verified":
                continue  # We're not returning or displaying this normal status
            data = self.serializer_class(badge).data
            data["workflow_status"] = status
            unverified_badges.append(data)

        if not mode:
            for x in (
                "task-completed",
                "verification-failed",
                "unknown",
                "planned",
                "deprecated",
            ):
                facet_key = x.replace("-", "_")
                if status_facet.get(facet_key, 0) > 0:
                    mode = x
                    break
            mode = mode or "task-completed"

        results = {
            "mode": mode,
            "status_facet": status_facet,
            "resourcebadges": unverified_badges,
        }

        if request.accepted_renderer.format == "html":
            return MyAPIResponse(
                {"results": results},
                template_name="integration_badges/badge_verification_status.html",
            )
        else:
            return MyAPIResponse({"results": results})


class Badge_Task_Full_v1(GenericAPIView):
    """
    Retrieve an Integration Task by ID
    """

    permission_classes = (ReadOnly,)
    authentication_classes = []
    renderer_classes = (JSONRenderer,)
    serializer_class = Badge_Task_Full_Serializer

    def get(self, request, *args, **kwargs):
        badge_id = kwargs.get("badge_id")
        if not badge_id:
            raise MyAPIException(
                code=status.HTTP_400_BAD_REQUEST, detail="Badge ID is required"
            )

        badge_tasks = Badge_Task.objects.filter(badge_id=badge_id).order_by(
            "sequence_no"
        )
        if badge_tasks.exists():
            serializer = self.serializer_class(
                badge_tasks, context={"request": request}, many=True
            )
            return MyAPIResponse({"results": serializer.data})
        else:
            # Return empty list if no tasks found, not an error
            return MyAPIResponse({"results": []})


class Resources_Eligible_List_v1(GenericAPIView):
    """
    Integration eligible CiDeR resources, which could be, are, or were integrated, but haven't been retired

    Based only on CiDeR since they may not have enrolled in a roadmap yet
    """

    permission_classes = (ReadOnly,)
    authentication_classes = []
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderInfrastructure_Summary_Serializer

    @extend_schema(
        responses=CiderInfrastructure_Summary_Serializer,
        parameters=[
            OpenApiParameter(
                name='organization_id',
                description='Organization ID',
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='info_resourceid',
                description='Info ResourceID',
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
            )
        ]
    )
    def get(self, request, format=None, **kwargs):
        organization_id = self.request.query_params.get('organization_id')
        info_resourceid = self.request.query_params.get('info_resourceid')

        resources = CiderInfrastructure.objects.filter(badging_filter)

        if organization_id is not None:
            resources = resources.filter(other_attributes__organizations__0__organization_id=int(organization_id))

        if info_resourceid is not None:
            resources = resources.filter(info_resourceid=info_resourceid)

        serializer = self.serializer_class(resources, context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})

class Organizations_Eligible_List_v1(GenericAPIView):
    '''
    List of distinct organizations that have Integration eligible CiDeR
    resources, which could be, are, or were integrated, but haven't been
    retired

    Based only on CiDeR since they may not have enrolled in a roadmap yet
    '''
    permission_classes = (ReadOnly,)
    authentication_classes = []
    renderer_classes = (JSONRenderer,)
    serializer_class = CiderOrganizations_Serializer

    def get(self, request, format=None, **kwargs):

        resources = CiderInfrastructure.objects.filter(badging_filter)
        org_ids = resources.values_list('other_attributes__organizations__0__organization_id', flat=True).distinct()
        orgs = CiderOrganizations.objects.filter(organization_id__in=[ int(org_id) for org_id in org_ids])

        serializer = self.serializer_class(orgs, context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})



class Resource_Full_v1(GenericAPIView):
    """
    Resource full details, including roadmaps, badges, and badge status
    """

    if DISABLE_PERMISSIONS_FOR_DEBUGGING:
        permission_classes = (AllowAny,)
    else:
        # permission_classes = [IsCoordinator | (IsAuthenticated & ReadOnly)]
        permission_classes = (ReadOnly,)
        authentication_classes = []

    renderer_classes = (JSONRenderer,)
    serializer_class = Resource_Full_Serializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='organization_id',
                description='Organization ID',
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='info_resourceid',
                description='Info ResourceID',
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
            )
        ]
    )
    def get(self, request, format=None, **kwargs):
        organization_id = self.request.query_params.get('organization_id')
        info_resourceid = self.request.query_params.get('info_resourceid')

        resources = CiderInfrastructure.objects.filter(badging_filter)

        if organization_id is not None:
            resources = resources.filter(other_attributes__organizations__0__organization_id=int(organization_id))

        if info_resourceid is not None:
            resources = resources.filter(info_resourceid=info_resourceid)

        serializer = self.serializer_class(resources, context={'request': request}, many=True)
        return MyAPIResponse({'results': serializer.data})


class Resource_Roadmap_Enrollments_v1(GenericAPIView):
    """
    Resource roadmap and roadmap badge enrollments
    """

    if DISABLE_PERMISSIONS_FOR_DEBUGGING:
        permission_classes = (AllowAny,)
    else:
        permission_classes = [
            IsCoordinator | IsConcierge | (IsAuthenticated & ReadOnly)
        ]

    renderer_classes = (JSONRenderer,)
    serializer_class = Resource_Enrollments_Serializer

    @extend_schema(
        responses=Resource_Enrollments_Response_Serializer,
    )
    def post(self, request, format=None, **kwargs):
        info_resourceid = kwargs.get("info_resourceid")
        if not info_resourceid:
            raise MyAPIException(
                code=status.HTTP_400_BAD_REQUEST, detail="Info_ResourceID is required"
            )
        roadmap_id = kwargs.get("roadmap_id")
        if not roadmap_id:
            raise MyAPIException(
                code=status.HTTP_400_BAD_REQUEST, detail="RoadmapID is required"
            )
        try:
            resource = CiderInfrastructure.objects.get(
                Q(info_resourceid=info_resourceid) & badging_filter
            )
            roadmap = Roadmap.objects.get(pk=roadmap_id)
        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(
                code=status.HTTP_404_NOT_FOUND,
                detail="Specified Info_ResourceID does not exist or is not eligible",
            )
        except Roadmap.DoesNotExist:
            raise MyAPIException(
                code=status.HTTP_404_NOT_FOUND, detail="Specified RoadmapID not found"
            )

        message = ""
        enroll_badges = []
        unenroll_badges = []

        # Enroll Resource in Roadmap if not already enrolled
        try:
            resource_roadmap = Resource_Roadmap.objects.get(
                info_resourceid=info_resourceid, roadmap=roadmap
            )
        except Resource_Roadmap.DoesNotExist:
            resource_roadmap = None
        except Exception as exc:
            raise MyAPIException(
                code=status.HTTP_400_BAD_REQUEST,
                detail="{}: {}".format(type(exc).__name__, exc),
            )
        if not resource_roadmap:
            try:
                resource_roadmap = Resource_Roadmap(
                    info_resourceid=info_resourceid, roadmap=roadmap
                ).save()
                message += f"Enrolled roadmap={roadmap.name}"
            except Exception as exc:
                raise MyAPIException(
                    code=status.HTTP_400_BAD_REQUEST,
                    detail="{}: {}".format(type(exc).__name__, exc),
                )

        # Check that badge_ids were specified
        raw_badge_ids = request.data.get("badge_ids")
        if not raw_badge_ids or type(raw_badge_ids) is not list:
            raise MyAPIException(
                code=status.HTTP_404_NOT_FOUND, detail="Missing BadgeIDs or not a list"
            )
        new_badge_ids = list(str(id) for id in raw_badge_ids)

        # Verify that each badge is available in the roadmap
        for id in new_badge_ids:
            try:
                new_roadmap_badge = Roadmap_Badge.objects.get(
                    roadmap_id=roadmap_id, badge_id=id
                )
            except Roadmap_Badge.DoesNotExist:
                raise MyAPIException(
                    code=status.HTTP_404_NOT_FOUND,
                    detail=f"Badge.ID ({id}) is not availabe in roadmap ({roadmap_id})",
                )

        # Retrieve current badges
        try:
            cur_badges = Resource_Badge.objects.filter(
                info_resourceid=info_resourceid, roadmap_id=roadmap_id
            )
            cur_badge_ids = [
                str(id) for id in cur_badges.values_list("badge_id", flat=True)
            ]
        except Exception as exc:
            raise MyAPIException(
                code=status.HTTP_400_BAD_REQUEST,
                detail="{}: {}".format(type(exc).__name__, exc),
            )

        # Check and enroll in badges
        for id in new_badge_ids:
            if id not in cur_badge_ids:
                try:
                    Resource_Badge(
                        info_resourceid=info_resourceid,
                        roadmap_id=roadmap_id,
                        badge_id=id,
                    ).save(username=get_current_username(request.user))
                except Exception as exc:
                    raise MyAPIException(
                        code=status.HTTP_400_BAD_REQUEST,
                        detail="{}: {}".format(type(exc).__name__, exc),
                    )
                enroll_badges.append(id)

        # Check and unenroll in badges
        for cur in cur_badges:
            if str(cur.badge_id) not in new_badge_ids:
                try:
                    cur.delete()
                except Exception as exc:
                    raise MyAPIException(
                        code=status.HTTP_400_BAD_REQUEST,
                        detail="{}: {}".format(type(exc).__name__, exc),
                    )
                unenroll_badges.append(str(cur.badge_id))

        if enroll_badges:
            message += "; " if message else ""
            message += f'Enrolled badges=({",".join(enroll_badges)})'
        if unenroll_badges:
            message += "; " if message else ""
            message += f'Unenrolled badges=({",".join(unenroll_badges)})'
        return MyAPIResponse({"message": message})


class Resource_Badge_Status_v1(GenericAPIView):
    """
    Record Badge Status
    """

    if DISABLE_PERMISSIONS_FOR_DEBUGGING:
        permission_classes = (AllowAny,)
    else:
        permission_classes = [
            IsCoordinator | IsImplementer | IsConcierge | (IsAuthenticated & ReadOnly)
        ]

    renderer_classes = (JSONRenderer,)
    serializer_class = Resource_Workflow_Post_Serializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="badge_workflow_status",
                description="Workflow status",
                type=str,
                required=True,
                location=OpenApiParameter.PATH,
                enum=BadgeWorkflowStatus,
                default=BadgeWorkflowStatus.PLANNED,
            )
        ],
        request=Resource_Workflow_Post_Serializer,
    )
    def post(self, request, badge_workflow_status, *args, **kwargs):
        info_resourceid = kwargs.get("info_resourceid")
        roadmap_id = kwargs.get("roadmap_id")
        badge_id = kwargs.get("badge_id")
        if (
            not info_resourceid
            or not roadmap_id
            or not badge_id
            or not badge_workflow_status
        ):
            raise MyAPIException(
                code=status.HTTP_400_BAD_REQUEST,
                detail="Info_ResourceID, Roadmap ID, Badge ID and status are required",
            )

        try:
            resource = CiderInfrastructure.objects.get(info_resourceid=info_resourceid)
            roadmap = Roadmap.objects.get(pk=roadmap_id)
            badge = Badge.objects.get(pk=badge_id)
            resource_badge = Resource_Badge.objects.get(
                info_resourceid=info_resourceid, roadmap=roadmap, badge=badge
            )
        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(
                code=status.HTTP_404_NOT_FOUND, detail="Specified resource not found"
            )
        except Roadmap.DoesNotExist:
            raise MyAPIException(
                code=status.HTTP_404_NOT_FOUND, detail="Specified roadmap not found"
            )
        except Badge.DoesNotExist:
            raise MyAPIException(
                code=status.HTTP_404_NOT_FOUND, detail="Specified badge not found"
            )
        except Resource_Badge.DoesNotExist:
            resource_badge = Resource_Badge(
                info_resourceid=info_resourceid, roadmap=roadmap, badge=badge
            )
            resource_badge.save(username=get_current_username(request.user))

        updated_by = request.data.get("status_updated_by")
        if not updated_by:
            updated_by = get_current_username(request.user)

        if badge_workflow_status is None:
            badge_workflow_status = resource_badge.status

        # Check what status is being set against permissions
        info_group_id = get_group_id(info_resourceid)
        can_post_status = False
        effective_role = ""

        if request.user.has_perm("Concierge"):
            can_post_status = True
        elif request.user.has_perm("cider.coordinator_" + info_group_id):
            effective_role = "cider.coordinator_" + info_group_id
            if badge_workflow_status in [
                BadgeWorkflowStatus.TASKS_COMPLETED,
                BadgeWorkflowStatus.PLANNED,
            ]:
                can_post_status = True
        elif request.user.has_perm("cider.implementer_" + info_group_id):
            effective_role = "cider.implementer_" + info_group_id
            if badge_workflow_status in [BadgeWorkflowStatus.TASKS_COMPLETED]:
                can_post_status = True
        else:
            can_post_status = False

        if can_post_status:
            workflow = Resource_Badge_Workflow(
                info_resourceid=info_resourceid,
                roadmap=roadmap,
                badge=badge,
                status=badge_workflow_status,
                status_updated_by=updated_by,
                comment=request.data.get("comment"),
            )
            workflow.save()

            return MyAPIResponse(
                {
                    "message": "Badge marked as %s" % badge_workflow_status,
                    "status_updated_at": workflow.status_updated_at,
                }
            )
        else:
            return MyAPIResponse(
                {
                    "message": "Role %s not allowed to set status %s"
                    % (effective_role, badge_workflow_status)
                },
                code=status.HTTP_403_FORBIDDEN,
            )


class Resource_Badge_Task_Status_v1(GenericAPIView):
    """
    Record Badge Task Status
    """

    if DISABLE_PERMISSIONS_FOR_DEBUGGING:
        permission_classes = (AllowAny,)
    else:
        permission_classes = [
            IsCoordinator | IsImplementer | IsConcierge | (IsAuthenticated & ReadOnly)
        ]

    renderer_classes = (JSONRenderer,)
    serializer_class = Resource_Workflow_Post_Serializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="badge_task_workflow_status",
                description="Filter by status",
                type=str,
                required=True,
                location=OpenApiParameter.PATH,
                enum=BadgeTaskWorkflowStatus,
                default=BadgeTaskWorkflowStatus.COMPLETED,
            )
        ],
        request=Resource_Workflow_Post_Serializer,
    )
    def post(self, request, badge_task_workflow_status, *args, **kwargs):
        info_resourceid = kwargs.get("info_resourceid")
        roadmap_id = kwargs.get("roadmap_id")
        badge_id = kwargs.get("badge_id")
        task_id = kwargs.get("task_id")
        if (
            not info_resourceid
            or not roadmap_id
            or not badge_id
            or not task_id
            or not badge_task_workflow_status
        ):
            raise MyAPIException(
                code=status.HTTP_400_BAD_REQUEST,
                detail="Info_ResourceID, Roadmap ID, Badge ID, Task ID and status are required",
            )

        try:
            resource = CiderInfrastructure.objects.get(info_resourceid=info_resourceid)
            roadmap = Roadmap.objects.get(pk=roadmap_id)
            badge = Badge.objects.get(pk=badge_id)
            task = Task.objects.get(pk=task_id)
            resource_badge = Resource_Badge.objects.get(
                info_resourceid=info_resourceid, roadmap=roadmap, badge=badge
            )
            badge_task = Badge_Task.objects.get(badge=badge, task=task)
        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(
                code=status.HTTP_404_NOT_FOUND, detail="Specified resource not found"
            )
        except Roadmap.DoesNotExist:
            raise MyAPIException(
                code=status.HTTP_404_NOT_FOUND, detail="Specified roadmap not found"
            )
        except Badge.DoesNotExist:
            raise MyAPIException(
                code=status.HTTP_404_NOT_FOUND, detail="Specified badge not found"
            )
        except Task.DoesNotExist:
            raise MyAPIException(
                code=status.HTTP_404_NOT_FOUND, detail="Specified task not found"
            )
        except Resource_Badge.DoesNotExist:
            raise MyAPIException(
                code=status.HTTP_404_NOT_FOUND,
                detail="Specified resource-badge relationship not found",
            )
        except Badge_task.DoesNotExist:
            raise MyAPIException(
                code=status.HTTP_404_NOT_FOUND,
                detail="Specified badge-task relationship not found",
            )

        updated_by = request.data.get("status_updated_by")
        if not updated_by:
            updated_by = get_current_username(request.user)

        if resource_badge.status in [BadgeWorkflowStatus.VERIFIED, BadgeWorkflowStatus.TASKS_COMPLETED] and badge_task_workflow_status != BadgeTaskWorkflowStatus.ACTION_NEEDED:
            workflow = Resource_Badge_Workflow(
                info_resourceid=info_resourceid,
                roadmap=roadmap,
                badge=badge,
                status=BadgeWorkflowStatus.PLANNED,
                status_updated_by=updated_by,
                comment=f"Reopened by the task (taskId={task_id}) '{task.name}'",
            )
            workflow.save()

        # Check what status is being set against permissions
        info_group_id = get_group_id(info_resourceid)
        can_post_status = False
        effective_role = ""

        if request.user.has_perm("Concierge"):
            can_post_status = True
        elif request.user.has_perm("cider.coordinator_" + info_group_id):
            effective_role = "cider.coordinator_" + info_group_id
            if badge_task_workflow_status in [
                BadgeTaskWorkflowStatus.TASKS_COMPLETED,
                BadgeTaskWorkflowStatus.NOT_COMPLETED,
            ]:
                can_post_status = True
        elif request.user.has_perm("cider.implementer_" + info_group_id):
            effective_role = "cider.implementer_" + info_group_id
            if badge_task_workflow_status in [
                BadgeTaskWorkflowStatus.TASKS_COMPLETED,
                BadgeTaskWorkflowStatus.NOT_COMPLETED,
            ]:
                can_post_status = True
        else:
            can_post_status = False

        if can_post_status:
            workflow = Resource_Badge_Task_Workflow(
                info_resourceid=info_resourceid,
                roadmap=roadmap,
                badge=badge,
                task=task,
                status=badge_task_workflow_status,
                status_updated_by=updated_by,
                comment=request.data.get("comment"),
            )
            workflow.save()

            return MyAPIResponse(
                {
                    "message": "Badge task marked as %s" % badge_task_workflow_status,
                    "status_updated_at": workflow.status_updated_at,
                }
            )
        else:
            return MyAPIResponse(
                {
                    "message": "Role %s not allowed to set task status %s"
                    % (effective_role, badge_task_workflow_status)
                },
                code=status.HTTP_403_FORBIDDEN,
            )


class Resource_Roadmap_Badge_Log_v1(GenericAPIView):
    """
    Retrieve all or one resource badge(s) and their status
    """

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
                name="info_resourceid",
                description="Info ResourceID",
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="roadmap_id",
                description="Roadmap ID",
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="badge_id",
                description="Badge ID",
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
            ),
        ]
    )
    def get(self, request, format=None, **kwargs):
        info_resourceid = self.request.query_params.get("info_resourceid")
        roadmap_id = self.request.query_params.get("roadmap_id")
        badge_id = self.request.query_params.get("badge_id")

        try:
            if info_resourceid is not None:
                resource = CiderInfrastructure.objects.get(
                    info_resourceid=info_resourceid
                )

            if roadmap_id is not None:
                roadmap = Roadmap.objects.get(pk=roadmap_id)

            if info_resourceid is not None and roadmap_id is not None:
                resource_roadmap = Resource_Roadmap.objects.get(
                    info_resourceid=info_resourceid, roadmap_id=roadmap_id
                )

            if badge_id is not None:
                badge = Badge.objects.get(pk=badge_id)

            if roadmap_id is not None and badge_id is not None:
                roadmap_badge = Roadmap_Badge.objects.get(
                    roadmap_id=roadmap_id, badge_id=badge_id
                )

        except CiderInfrastructure.DoesNotExist:
            raise MyAPIException(
                code=status.HTTP_404_NOT_FOUND,
                detail="Specified Info_ResourceID not found",
            )
        except Roadmap.DoesNotExist:
            raise MyAPIException(
                code=status.HTTP_404_NOT_FOUND, detail="Specified RoadmapID not found"
            )
        except Resource_Roadmap.DoesNotExist:
            raise MyAPIException(
                code=status.HTTP_404_NOT_FOUND,
                detail="Specified resource-roadmap relationship not found not found",
            )
        except Badge.DoesNotExist:
            raise MyAPIException(
                code=status.HTTP_404_NOT_FOUND, detail="Specified BadgeID not found"
            )
        except Roadmap_Badge.DoesNotExist:
            raise MyAPIException(
                code=status.HTTP_404_NOT_FOUND,
                detail="Specified roadmap-badge relationship not found not found",
            )

        badges_status = []

        resource_roadmaps = Resource_Roadmap.objects.all()
        if info_resourceid is not None:
            resource_roadmaps = resource_roadmaps.filter(
                info_resourceid=info_resourceid
            )
        if roadmap_id is not None:
            resource_roadmaps = resource_roadmaps.filter(roadmap_id=roadmap_id)

        for resource_roadmap in resource_roadmaps:
            roadmap_badges = Roadmap_Badge.objects.all().filter(
                roadmap_id=resource_roadmap.roadmap_id
            )
            if badge_id is not None:
                roadmap_badges = roadmap_badges.filter(badge_id=badge_id)

            for roadmap_badge in roadmap_badges:
                resource_badge_logs = (
                    Resource_Badge_Workflow.objects.all()
                    .filter(
                        info_resourceid=resource_roadmap.info_resourceid,
                        roadmap_id=resource_roadmap.roadmap_id,
                        badge_id=roadmap_badge.badge_id,
                    )
                    .order_by("-status_updated_at")
                )

                for resource_badge_log in resource_badge_logs:
                    badge_status = {
                        "id": resource_badge_log.workflow_id,
                        "info_resourceid": resource_badge_log.info_resourceid,
                        "roadmap_id": resource_badge_log.roadmap_id,
                        "badge_id": resource_badge_log.badge_id,
                        "status": resource_badge_log.status,
                        "status_updated_by": resource_badge_log.status_updated_by,
                        "status_updated_at": resource_badge_log.status_updated_at,
                        "comment": resource_badge_log.comment,
                    }
                    badges_status.append(badge_status)
        return MyAPIResponse({"results": badges_status})


class Resource_Roadmap_Badges_Status_Summary_v1(GenericAPIView):
    """
    Retrieve all or one resource badge(s) and their status
    """

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
                name='organization_id',
                description='Organization ID',
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='info_resourceid',
                description='Info ResourceID',
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="roadmap_id",
                description="Roadmap ID",
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="badge_id",
                description="Badge ID",
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
            ),
        ]
    )
    def get(self, request, format=None, **kwargs):
        organization_id = self.request.query_params.get('organization_id')
        info_resourceid = self.request.query_params.get('info_resourceid')
        roadmap_id = self.request.query_params.get('roadmap_id')
        badge_id = self.request.query_params.get('badge_id')

        resource_subquery  = CiderInfrastructure.objects#.filter(badging_filter)
        resource_badge_workflow_subquery = Resource_Badge_Workflow.objects

        if organization_id is not None:
            resource_subquery = resource_subquery.filter(other_attributes__organizations__0__organization_id=int(organization_id))

        if info_resourceid is not None:
            resource_badge_workflow_subquery = resource_badge_workflow_subquery.filter(info_resourceid=info_resourceid)

        if roadmap_id is not None:
            resource_badge_workflow_subquery = resource_badge_workflow_subquery.filter(
                roadmap_id=roadmap_id
            )

        if badge_id is not None:
            resource_badge_workflow_subquery = resource_badge_workflow_subquery.filter(
                badge_id=badge_id
            )

        result = (
            resource_badge_workflow_subquery.filter(

                # Making sure the resource if a part of the organization
                Exists(resource_subquery.filter(
                    info_resourceid=OuterRef('info_resourceid')
                )),

                # Making sure the badge is a part of the roadmap
                Exists(
                    Roadmap_Badge.objects.filter(
                        roadmap_id=OuterRef("roadmap_id"), badge_id=OuterRef("badge_id")
                    )
                ),
                # Making sure the resource is enrolled to the roadmap badge
                Exists(
                    Resource_Badge.objects.filter(
                        info_resourceid=OuterRef("info_resourceid"),
                        roadmap_id=OuterRef("roadmap_id"),
                        badge_id=OuterRef("badge_id"),
                    )
                ),
                # Filtering the workflow entries with the latest time stamp
                status_updated_at=Subquery(
                    Resource_Badge_Workflow.objects.filter(
                        info_resourceid=OuterRef("info_resourceid"),
                        roadmap_id=OuterRef("roadmap_id"),
                        badge_id=OuterRef("badge_id"),
                    )
                    .values("info_resourceid", "roadmap_id", "badge_id")
                    .annotate(max_status_updated_at=Max("status_updated_at"))
                    .values("max_status_updated_at")
                ),
            )
            .values("status")
            .annotate(count=Count("workflow_id"))
        )

        return MyAPIResponse({"results": result.values("status", "count")})


class Resource_Roadmap_Badges_Status_v1(GenericAPIView):
    """
    Retrieve all or one resource badge(s) and their status
    """

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
                name="info_resourceid",
                description="Info ResourceID",
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="roadmap_id",
                description="Roadmap ID",
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="badge_id",
                description="Badge ID",
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="badge_workflow_status",
                description="Badge Workflow Status",
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
                enum=BadgeWorkflowStatus,
            ),
        ]
    )
    def get(self, request, format=None, **kwargs):
        info_resourceid = self.request.query_params.get("info_resourceid")
        roadmap_id = self.request.query_params.get("roadmap_id")
        badge_id = self.request.query_params.get("badge_id")
        badge_workflow_status = self.request.query_params.get("badge_workflow_status")

        resource_badge_workflow_subquery = Resource_Badge_Workflow.objects

        if info_resourceid is not None:
            resource_badge_workflow_subquery = resource_badge_workflow_subquery.filter(
                info_resourceid=info_resourceid
            )

        if roadmap_id is not None:
            resource_badge_workflow_subquery = resource_badge_workflow_subquery.filter(
                roadmap_id=roadmap_id
            )

        if badge_id is not None:
            resource_badge_workflow_subquery = resource_badge_workflow_subquery.filter(
                badge_id=badge_id
            )

        if badge_workflow_status is not None:
            resource_badge_workflow_subquery = resource_badge_workflow_subquery.filter(
                status=badge_workflow_status
            )

        resource_badge_subquery = Resource_Badge.objects.filter(
            info_resourceid=OuterRef("info_resourceid"),
            roadmap_id=OuterRef("roadmap_id"),
            badge_id=OuterRef("badge_id"),
        )

        result = (
            resource_badge_workflow_subquery.filter(
                # Making sure the badge is a part of the roadmap
                Exists(
                    Roadmap_Badge.objects.filter(
                        roadmap_id=OuterRef("roadmap_id"), badge_id=OuterRef("badge_id")
                    )
                ),
                # Making sure the resource is enrolled to the roadmap badge
                Exists(
                    Resource_Badge.objects.filter(
                        info_resourceid=OuterRef("info_resourceid"),
                        roadmap_id=OuterRef("roadmap_id"),
                        badge_id=OuterRef("badge_id"),
                    )
                ),
                # Filtering the workflow entries with the latest time stamp
                status_updated_at=Subquery(
                    Resource_Badge_Workflow.objects.filter(
                        info_resourceid=OuterRef("info_resourceid"),
                        roadmap_id=OuterRef("roadmap_id"),
                        badge_id=OuterRef("badge_id"),
                    )
                    .values("info_resourceid", "roadmap_id", "badge_id")
                    .annotate(max_status_updated_at=Max("status_updated_at"))
                    .values("max_status_updated_at")
                ),
            )
            # Including the badge access url and label from the resource badge table
            .annotate(
                badge_access_url=Subquery(
                    resource_badge_subquery.values("badge_access_url")
                )
            )
            .annotate(
                badge_access_url_label=Subquery(
                    resource_badge_subquery.values("badge_access_url_label")
                )
            )
            .order_by("-status_updated_at", "info_resourceid", "roadmap_id", "badge_id")
        )

        return MyAPIResponse({"results": result.values()})


class Resource_Roadmap_Badge_Tasks_Status_v1(GenericAPIView):
    """
    Retrieve details of a specific resource, including roadmaps and their badges.
    It also includes the list of badge statuses of the badges that are at least planned.
    """

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
                name="info_resourceid",
                description="Info ResourceID",
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="roadmap_id",
                description="Roadmap ID",
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="badge_id",
                description="Badge ID",
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="task_id",
                description="Task ID",
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="badge_task_workflow_status",
                description="Badge Task Workflow Status",
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
                enum=BadgeTaskWorkflowStatus,
            ),
        ]
    )
    def get(self, request, format=None, **kwargs):
        info_resourceid = self.request.query_params.get("info_resourceid")
        roadmap_id = self.request.query_params.get("roadmap_id")
        badge_id = self.request.query_params.get("badge_id")
        task_id = self.request.query_params.get("task_id")
        badge_task_workflow_status = self.request.query_params.get(
            "badge_task_workflow_status"
        )

        resource_badge_task_workflow_subquery = Resource_Badge_Task_Workflow.objects

        if info_resourceid is not None:
            resource_badge_task_workflow_subquery = (
                resource_badge_task_workflow_subquery.filter(
                    info_resourceid=info_resourceid
                )
            )

        if roadmap_id is not None:
            resource_badge_task_workflow_subquery = (
                resource_badge_task_workflow_subquery.filter(roadmap_id=roadmap_id)
            )

        if badge_id is not None:
            resource_badge_task_workflow_subquery = (
                resource_badge_task_workflow_subquery.filter(badge_id=badge_id)
            )

        if task_id is not None:
            resource_badge_task_workflow_subquery = (
                resource_badge_task_workflow_subquery.filter(task_id=task_id)
            )

        if badge_task_workflow_status is not None:
            resource_badge_task_workflow_subquery = (
                resource_badge_task_workflow_subquery.filter(
                    status=badge_task_workflow_status
                )
            )

        result = resource_badge_task_workflow_subquery.filter(
            # Making sure the badge is a part of the roadmap
            Exists(
                Roadmap_Badge.objects.filter(
                    roadmap_id=OuterRef("roadmap_id"), badge_id=OuterRef("badge_id")
                )
            ),
            # Making sure the task is a part of the badge
            Exists(
                Badge_Task.objects.filter(
                    badge_id=OuterRef("badge_id"), task_id=OuterRef("task_id")
                )
            ),
            # Making sure the resource is enrolled to the roadmap badge
            Exists(
                Resource_Badge.objects.filter(
                    info_resourceid=OuterRef("info_resourceid"),
                    roadmap_id=OuterRef("roadmap_id"),
                    badge_id=OuterRef("badge_id"),
                )
            ),
            # Filtering the workflow entries with the latest time stamp
            status_updated_at=Subquery(
                Resource_Badge_Task_Workflow.objects.filter(
                    info_resourceid=OuterRef("info_resourceid"),
                    roadmap_id=OuterRef("roadmap_id"),
                    badge_id=OuterRef("badge_id"),
                    task_id=OuterRef("task_id"),
                )
                .values("info_resourceid", "roadmap_id", "badge_id", "task_id")
                .annotate(max_status_updated_at=Max("status_updated_at"))
                .values("max_status_updated_at")
            ),
        ).order_by(
            "-status_updated_at", "info_resourceid", "roadmap_id", "badge_id", "task_id"
        )

        return MyAPIResponse({"results": result.values()})


class DatabaseFile_v1(GenericAPIView):
    """
    Retrieve tasks of a specific badge.
    """

    permission_classes = (ReadOnly,)
    authentication_classes = []
    renderer_classes = (JSONRenderer,)
    serializer_class = DatabaseFile_Serializer

    def get(self, request, *args, **kwargs):
        file_id = kwargs.get("file_id")
        if not file_id:
            raise MyAPIException(
                code=status.HTTP_400_BAD_REQUEST, detail="File ID is required"
            )

        try:
            file = DatabaseFile.objects.get(pk=file_id)
        except DatabaseFile.DoesNotExist:
            raise MyAPIException(
                code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )

        response = HttpResponse(file.file_data, content_type=file.content_type)
        response["Content-Disposition"] = 'inline; filename="%s"' % file.file_name

        return response
