#!/bin/bash
APP_HOME="/soft/warehouse-2.0"
APP_NAME="warehouse_api"
APP_DJANGO="/soft/warehouse-2.0/PROD/Operations_Warehouse_Django"

export APP_CONFIG=$APP_HOME/conf/django_prod_mgmt.conf
cd $APP_DJANGO
exec python3 manage.py "$@"
