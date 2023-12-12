#!/bin/bash

#./local_scripts/get_latest_backup.sh
cp postgresql_setup_customized.sql dbrestore/postgresql_setup.sql
docker exec -it docker_django_1 /opt/app/scripts/resetdb.sh
docker exec -it docker_django_1 /opt/app/scripts/populatedb.sh

