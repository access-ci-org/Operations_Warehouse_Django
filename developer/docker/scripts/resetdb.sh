#!/bin/bash

#docker exec -it $1 /usr/bin/psql -U opsdba -h localhost -p 5432 postgres -f postgresql_setup.sql
/usr/bin/psql -U opsdba -h db -p 5432 postgres -f /opt/app/dbrestore/postgresql_setup.sql
