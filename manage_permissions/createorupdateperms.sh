#!/bin/bash
APP_HOME="/soft/warehouse-2.0"
APP_NAME="warehouse_api"
APP_DJANGO="/soft/warehouse-2.0/PROD/Operations_Warehouse_Django"

cd $APP_HOME/sbin
./manage.api.sh shell <./createorupdateperms.py
