from django.contrib.auth.models import Group
from cider.models import CiderGroups
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

content_type = ContentType.objects.get_for_model(CiderGroups)

# Create RoadmapMaintainer permission and group
#try:
#    permission = Permission.objects.update_or_create(codename="roadmap_maintainer", name='RoadmapMaintainer', content_type=content_type)
#except Exception as e:
#    print(f"Something went wrong creating/updating RoadmapMaintainer permission: {e}")

# Create BadgeMaintainer permission and group
#try:
#    permission = Permission.objects.update_or_create(codename="badge_maintainer", name='BadgeMaintainer', content_type=content_type)
#except Exception as e:
#    print(f"Something went wrong creating/updating BadgeMaintainer permission: {e}")

# Create Concierge permission and group
#try:
#    permission = Permission.objects.update_or_create(codename="concierge", name='Concierge', content_type=content_type)
#except Exception as e:
#    print(f"Something went wrong creating/updating Concierge permission: {e}")

#Create/update ACCESS Staff permission
try:
    sname=f"Project staff for access-ci.org"
    cname=f"project.staff_access-ci.org"

    project_access_staff_permission, perm_status = Permission.objects.update_or_create(codename=cname, defaults={'name':sname, 'content_type':content_type})

except Exception as e:
    print(f"problem creating/updating all access staff permission {e}")

#Create/update ACCESS RP Staff permission
try:
    sname=f"RP Staff for access-ci.org"
    cname=f"rp.staff_access-ci.org"

    rp_access_staff_permission, perm_status = Permission.objects.update_or_create(codename=cname, defaults={'name':sname, 'content_type':content_type})

except Exception as e:
    print(f"problem creating/updating all RP access staff permission {e}")

#Create/update ALL staff permission
try:
    sname=f"All staff for access-ci.org"
    cname=f"all.staff_access-ci.org"

    all_access_staff_permission, perm_status = Permission.objects.update_or_create(codename=cname, defaults={'name':sname, 'content_type':content_type})

except Exception as e:
    print(f"problem creating/updating all access staff (project and RP) permission {e}")

for role in ["implementer", "coordinator","staff"]:
    print(f"Creating or updating for {role} role")
    for obj in CiderGroups.objects.all():
        try:
            cname = role+'_'+str(obj.info_groupid)
            sname = str.capitalize(role)+' for ' + str(obj.info_groupid)

            permission, perm_status = Permission.objects.update_or_create(codename=cname, defaults={'name':sname, 'content_type':content_type})
            #permission = Permission.objects.update_or_create(codename=role+'_'+str(obj.info_groupid), name='Implementer for ' + str(obj.info_groupid), content_typer=:content_type, defaults={'codename':role+'_'+str(obj.info_groupid), 'name':'Implementer for ' + str(obj.info_groupid), 'content_type':content_type})
            newgroup, status = Group.objects.update_or_create(name='urn:group:access-ci.org:'+obj.info_groupid+':'+role)
            try:
                newgroup.permissions.get(codename=cname, content_type=content_type)
                newgroup.permissions.get(codename="all.staff_access-ci.org", content_type=content_type)
                newgroup.permissions.get(codename="rp.staff_access-ci.org", content_type=content_type)
            except Exception as e:
                print(f"problem getting permissions from group: {e}")
                print(f"group in question is:{newgroup}")
                print(f"permission in question is:{cname}")
                newgroup.permissions.add(permission)
                newgroup.permissions.add(all_access_staff_permission)
                newgroup.permissions.add(rp_access_staff_permission)
                # If this is the staff role, we need to add
                # all staff and RP staff permissions to the group
                #if role=="staff":

            #if not newgroup.permissions.contains(permission):
            #    newgroup.permissions.add(permission)
        except Exception as e:
            print(f"problem updating group permission {e}")


for role in ["concierge","badge.maintainer", "roadmap.maintainer"]:
    print(f"Creating or updating for {role} role")
    try:
        #sname = str.capitalize(role)
        sname=''
        snamelist = role.split(".")
        for part in snamelist:
            sname += str.capitalize(part)

        permission, perm_status = Permission.objects.update_or_create(codename=role, defaults={'name':sname, 'content_type':content_type})
        newgroup, status = Group.objects.update_or_create(name='urn:group:access-ci.org:operations.access-ci.org:'+role)
        try:
            newgroup.permissions.get(codename=role, content_type=content_type)
            newgroup.permissions.get(codename="all.staff_access-ci.org", content_type=content_type)
        except Exception as e:
            print(f"problem getting permissions from group: {e}")
            print(f"group in question is:{newgroup}")
            print(f"permission in question is:{cname}")
            newgroup.permissions.add(permission)
            newgroup.permissions.add(all_access_staff_permission)

        #if not newgroup.permissions.contains(permission):
        #    newgroup.permissions.add(permission)
    except Exception as e:
        print(f"problem updating group permission {e}")

# Create or update all ACCESS-CI staff permissions per project

for project in ["aco", "allocations", "support", "metrics", "operations"]:
    print(f"Creating or updating staff roles for project {project}")
    try:
        sname=f"Staff for {project}.access-ci.org"
        cname=f"staff_{project}.access-ci.org"

        permission, perm_status = Permission.objects.update_or_create(codename=cname, defaults={'name':sname, 'content_type':content_type})
        newgroup, status = Group.objects.update_or_create(name='urn:group:access-ci.org:'+project+'.access-ci.org:staff')
        try:
            newgroup.permissions.get(codename=cname, content_type=content_type)
            newgroup.permissions.get(codename="all.staff_access-ci.org", content_type=content_type)
            newgroup.permissions.get(codename="project.staff_access-ci.org", content_type=content_type)
        except Exception as e:
            print(f"problem getting permissions from group: {e}")
            print(f"group in question is:{newgroup}")
            print(f"permission in question is:{cname}")
            newgroup.permissions.add(permission)
            newgroup.permissions.add(all_access_staff_permission)
            newgroup.permissions.add(project_access_staff_permission)

        #if not newgroup.permissions.contains(permission):
        #    newgroup.permissions.add(permission)
    except Exception as e:
        print(f"problem updating group permission {e}")
        
for obj in Permission.objects.all():
    print(obj.name, obj.codename)
