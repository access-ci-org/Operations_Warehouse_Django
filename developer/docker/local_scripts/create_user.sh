#!/bin/bash
docker exec -it warehouse_django  /soft/warehouse-2.0/sbin/manage.users.sh createsuperuser
