#!/bin/bash
docker exec -it warehouse_django /opt/app/scripts/get_latest_backup.sh django.warehouse_stg.mindump
