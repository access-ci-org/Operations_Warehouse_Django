#!/bin/bash
docker exec -it docker-django-1  /soft/warehouse-2.0/sbin/manage.users.sh createsuperuser
