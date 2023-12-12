Prerequisites:
* A functional docker and docker-compose ecosystem.
* The django_aws_credential_key file, in your home dir.  Get this from Eric or JP.
* Your local uid and gid (on linux systems, you can use the "id" command to get these)


Quick notes for using the docker-compose django dev environment:

Inital steps:

Copy env_template to .env, and change the password, UID, and GID values

mkdir -p data/db

docker build -f ./warehouse.yml -t warehouse:latest .

docker-compose -f warehouse_deploy.yml up

NOTE: For all of the below commands, if you are using docker-compose v1, you will need to use the *-dc1.sh scripts in ./local_scripts, as docker-compose v1 uses underscores "_" instead of hyphens "-" in the container names.

./local_scripts/decrypt_credentials

Set the info_django and warehouse_user password to a value you like:
./local_scripts/set_warehouse_pw.sh <password you want to set>

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


Still todo:  add the opensearch container to warehouse_deploy.yml

Bullet changes:
Defines containers for warehouse code and warehouse db
Provides scripts to initialize db from backup
