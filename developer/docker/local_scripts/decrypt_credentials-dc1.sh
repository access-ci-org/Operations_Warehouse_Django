#!/bin/bash
docker exec -it docker_django_1 ansible-vault decrypt --vault-id /opt/app/django_aws_credential_key /opt/app/aws_credentials --output /opt/app/aws_credentials_local
