from django.contrib.auth.models import Group
from cider.models import CiderGroups
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

content_type = ContentType.objects.get_for_model(CiderGroups)

#for obj in CiderGroups.objects.all():

for group in Group.objects.all():
    print(group.name)
    print(group.permissions.all())

for perm in Permission.objects.all():
    print(perm.__dict__)
