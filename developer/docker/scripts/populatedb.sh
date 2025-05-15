#!/bin/bash

#docker exec -it $1 psql -U info_django -h localhost -p 5432 warehouse2 -f /opt/app/dbrestore/db.backup
#docker exec -it $1 psql -U info_django -h localhost -p 5432 warehouse2 -f /opt/app/dbrestore/django.dump.1701118801
psql -U opsdba -h db -p 5432 warehouse2 -f /opt/app/dbrestore/django.dump.latest
