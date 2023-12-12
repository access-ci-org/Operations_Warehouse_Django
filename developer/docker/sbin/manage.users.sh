#! /bin/sh
APP_NAME=warehouse_api
APP_HOME=/soft/warehouse-2.0
APP_SOURCE_NAME=Operations_Warehouse_Django

export APP_CONFIG=$APP_HOME/conf/$APP_NAME.conf
export DJANGO_CONFIG=$APP_HOME/conf/$APP_NAME.conf
#exec $APP_HOME/python/bin/gunicorn --config=$APP_HOME/conf/$APP_NAME.gunicorn.conf.py $APP_SOURCE_NAME.wsgi:application
APP_DJANGO="/soft/warehouse-2.0/PROD/Operations_Warehouse_Django"
cd $APP_DJANGO
exec python3 manage.py $@
