The contents of this directory, described by this document will configure a
development environment for ACCESS-CI Operations Warehouse.

This environment uses docker and docker-compose to configure several containers.
One container consists of the configured Postgresql server that the warehouse requires.
Another container consists of the Django deployment of the warehouse itself,
along with its prerequisites and various scripts for confguring and/or interacting
with it.


# How to setup the docker-compose django dev environment

## Prerequisites:
* A functional docker and docker-compose ecosystem.
* The django_aws_credential_key file, in your home dir.  Get this from Eric or JP.
* Your local uid and gid (on linux systems, you can use the "id" command to get these)
* Docker vm.max_map_count >= 262144 (See also: faq.md)

## Initial steps:

* Setup .env:
  * `cp env_template .env`
  * `vim .env`
    * Change the password, UID, and GID values (these are the numeric IDs, not the names)

* Set a password for info_django and warehouse_user:
  * `./local_scripts/set_warehouse_pw.sh <A_SECURE_RANDOM_PASSWORD>`

* Create the DB dir
  * `mkdir -p data/db`

* Build the local image
  * `docker build -t warehouse:latest --progress=plain --no-cache . 2>&1 | tee build_warehouse.log`

* Start the containers
  * `docker-compose up -d`

* Decrypt credentials:
  * `./local_scripts/decrypt_credentials.sh`

* Get the latest production data backup, and initialize the database:
  * `./local_scripts/get_backup_on_container.sh`
  * `./local_scripts/initialize_db.sh`

* Start your dev environment on localhost:8000
  * `./local_scripts/runserver.sh`

* (OPTIONAL) Open a bash shell on the django warehouse container
  * `./local_scripts/bash_on_django_container.sh`


# Other Useful Commands

### If you need to reset your database:
```
docker compose down
rm -rf data/db
mkdir -p data/db
docker compose up -d
./local_scripts/initialize_db.sh
```

### To create a superuser account that can do anything needed in the admin interface:
```
./local_scripts/create_user.sh
```


# TODO
* add the opensearch container to warehouse_deploy.yml


# Bullet changes:
* Defines containers for warehouse code and warehouse db
* Provides scripts to initialize db from backup
