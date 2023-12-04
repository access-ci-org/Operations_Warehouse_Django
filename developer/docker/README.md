Quick notes for using the docker-compose django dev environment:

Inital steps:
Copy env_template to .env, and change the password, UID, and GID values

ansible-vault decrypt --vault-id ~/ansible_vault_password aws_credentials --output aws_credentials_local

docker build -f ./warehouse.yml -t warehouse:latest .
docker-compose -f warehouse_deploy.yml up
./local_scripts/get_latest_backup.sh
./local_scripts/initialize_db.sh


then ./local_scripts/runserver.sh will start your dev env on localhost:8000,
and ./local_scripts/bash_on_django_container.sh will open a bash shell on the django warehouse container.

Still todo:  add the opensearch container to warehouse_deploy.yml

Bullet changes:
Defines containers for warehouse code and warehouse db
Provides scripts to initialize db from backup
