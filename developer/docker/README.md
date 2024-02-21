The contents of this directory, described by this document will configure a 
development environment for ACCESS-CI Operations Warehouse.

This environment uses docker and docker-compose to configure several containers.
One container consists of the configured Postgresql server that the warehouse requires
Another container consists of the Django deployment of the warehouse itself, along with its prerequisites and various scripts for confguring and/or interacting
with it.


Prerequisites:
* A functional docker and docker-compose ecosystem.
* The django_aws_credential_key file, in your home dir.  Get this from Eric or JP.
* Your local uid and gid (on linux systems, you can use the "id" command to get these)


Quick notes for using the docker-compose django dev environment:

Inital steps:

Copy env_template to .env, and change the password, UID, and GID values

mkdir -p data/db

Set the info_django and warehouse_user password to a value you like:
./local_scripts/set_warehouse_pw.sh <password you want to set>

docker build -f ./warehouse.yml -t warehouse:latest .

docker-compose -f warehouse_deploy.yml up

NOTE: For all of the below commands, if you are using docker-compose v1, you will need to use the *-dc1.sh scripts in ./local_scripts, as docker-compose v1 uses underscores "_" instead of hyphens "-" in the container names.

./local_scripts/decrypt_credentials

Get the latest production data backup, and initialize the database:

./local_scripts/get_backup_on_container.sh
./local_scripts/initialize_db.sh

then ./local_scripts/runserver.sh will start your dev env on localhost:8000,
and ./local_scripts/bash_on_django_container.sh will open a bash shell on the django warehouse container.

If you need to reset your database:
docker-compose -f warehouse_deploy.yml down
rm -rf data/db
mkdir -p data/db
docker-compose -f warehouse_deploy.yml up
./local_scripts/initialize_db.sh


To create a superuser account that can do anything needed in the admin interface:

./local_scripts/create_user.sh


Still todo:  add the opensearch container to warehouse_deploy.yml

Bullet changes:
Defines containers for warehouse code and warehouse db
Provides scripts to initialize db from backup
