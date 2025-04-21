import re
from rest_framework import permissions
from cider.serializers import *
from rest_framework.permissions import BasePermission, SAFE_METHODS

class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class ResourceIDError(Exception):
    """Exception raised when info_resourceid not found in CiderGroups.

    Attributes:
        message -- which info_resourceid not found
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"

class IsBadgeRole(permissions.BasePermission):
    """This is a base class that implements the logic for authz for Badge Roles"""
    def __init__(self, rolename=''):
        self.rolename = rolename

    def has_permission(self, request, view):
        info_resourceid = request.parser_context["kwargs"]['info_resourceid']
        resource = CiderInfrastructure.objects.get(pk=info_resourceid)
        info_resourceid = resource.info_resourceid
        try:
            cidergroup = CiderGroups.objects.filter(info_resourceids__contains=[info_resourceid]).first()
        except:
            return False
        if not cidergroup:
            raise(ResourceIDError(f"{info_resourceid} not found in any CiderGroup"))
            return False
        else:
            info_groupid = cidergroup.info_groupid
        # Do we want different perms here for read only?
        # Read permissions are allowed to any request.
        #if request.method in ['GET', 'HEAD', 'OPTIONS']:
        #if request.method in ['HEAD', 'OPTIONS']:
        #    return True

        # Write permissions are only allowed to the owner.
        if request.user.is_authenticated:
            #print(f'User {request.user.username} is authenticated')
            #print(f'User permissions {request.user.get_all_permissions()}')
            return request.user.has_perm('cider.'+self.rolename+'_'+info_groupid)
        else:
            return False




class IsRoadmapMaintainer(IsBadgeRole):
    """This is an example that authorizes all authenticated users"""
    def __init__(self, rolename):
        super().__init__(rolename)
        self.rolename = 'roadmap_maintainer'

class IsImplementer(IsBadgeRole):
    """This is an example that authorizes all authenticated users"""
    def __init__(self, rolename):
        super().__init__(rolename)
        self.rolename = 'implementer'

class IsCoordinator(IsBadgeRole):
    """This is an example that authorizes all authenticated users"""
    def __init__(self, rolename='coordinator'):
        super().__init__(rolename)
        self.rolename = 'coordinator'

class IsFooCoordinator(permissions.BasePermission):
    """This is an example that authorizes all authenticated users"""
    def has_permission(self, request, view):
        info_resourceid = request.parser_context["kwargs"]['info_resourceid']
        resource = CiderInfrastructure.objects.get(pk=info_resourceid)
        info_resourceid = resource.info_resourceid
        cleaned_resourceid = re.sub(r'xsede\.org', 'access-ci.org', info_resourceid)
        cidergroup = CiderGroups.objects.filter(info_resourceids__contains=[cleaned_resourceid]).first()
        info_groupid = cidergroup.info_groupid
        # Do we want different perms here for read only?
        # Read permissions are allowed to any request.
        #if request.method in ['GET', 'HEAD', 'OPTIONS']:
        #if request.method in ['HEAD', 'OPTIONS']:
        #    return True

        # Write permissions are only allowed to the owner.
        if request.user.is_authenticated:
            print(f'User {request.user.username} is authenticated')
            print(f'User permissions {request.user.get_all_permissions()}')
            print(f'info_groupid is  {info_groupid}')
            print('cider.coordinator'+'_'+info_groupid)
            return request.user.has_perm('cider.coordinator'+'_'+info_groupid)
        else:
            return False
