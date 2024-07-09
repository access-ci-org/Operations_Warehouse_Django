#!/bin/bash

APP_NAME=warehouse_api
APP_HOME=/soft/warehouse-2.0
APP_SOURCE_NAME=Operations_Warehouse_Django
export APP_CONFIG=$APP_HOME/conf/$APP_NAME.conf
export DJANGO_CONFIG=$APP_HOME/conf/$APP_NAME.conf

docker exec -it \
  -e "APP_CONFIG=$APP_HOME/conf/$APP_NAME.conf" \
  -e "DJANGO_CONFIG=$APP_HOME/conf/$APP_NAME.conf" \
  docker-django-1 /bin/bash
