from django.contrib.auth.models import Group
from cider.models import CiderGroups
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

content_type = ContentType.objects.get_for_model(CiderGroups)

# Create RoadmapMaintainer permission and group
try
    permission = Permission.objects.get(codename="roadmap_maintainer", name='RoadmapMaintainer', content_type=content_type)
except Permission.DoesNotExist:
    try:
        permission = Permission.objects.create(codename="roadmap_maintainer", name='RoadmapMaintainer', content_type=content_type)
    except:
        pass

for role in ["implementer", "coordinator"]:
    for obj in CiderGroups.objects.all():
        try:
            permission = Permission.objects.get(codename=role+'_'+str(obj.info_groupid), name='Implementer for ' + str(obj.info_groupid), content_type=content_type)
        except Permission.DoesNotExist:
            try:
                permission = Permission.objects.create(codename=role+'_'+str(obj.info_groupid), name=role+' for ' + str(obj.info_groupid), content_type=content_type)
            except:
                pass
        try:
            newgroup = Group.objects.get(name='urn:group:access-ci.org:'+obj.info_groupid+':'+role)
        except Group.DoesNotExist:
            try:
                newgroup = Group.objects.create(name='urn:group:access-ci.org:'+obj.info_groupid+':'+role)
                newgroup.permissions.add(permission)
            except:
                pass


for obj in Permission.objects.all():
    print(obj.name)
