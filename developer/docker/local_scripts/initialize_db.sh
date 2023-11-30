#!/bin/bash

./local_scripts/get_latest_backup.sh
docker exec -it docker-django-1 /opt/app/scripts/reset_db.sh
docker exec -it docker-django-1 /opt/app/scripts/populate_db.sh

