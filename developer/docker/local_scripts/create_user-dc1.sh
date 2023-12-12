#!/bin/bash
docker exec -it docker_django_1  /soft/warehouse-2.0/sbin/manage.users.sh createsuperuser
