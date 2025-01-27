# Warehouse Python Environments

Produced while exploring possible use of https://docs.astral.sh/uv/

## warehouse-django

**Common packages**

python_version = "3.10"

django = "==5.0.*"
psycopg2-binary = "*"
django-opensearch-dsl = "==0.5.*"
pip-versions = "*"

## warehouse-api 

**Add to warehouse-django**

django-cors-headers = "*"
django-allauth = "==0.52.*"
django-bootstrap5 = "==24.*"
djangorestframework = "*"
drf-spectacular = "*"
gunicorn = "==22.*"
markdown = "*"
mod-wsgi = "*"
Pillow = "*"
python-jose = "*"
python3-openid = "*"
pymemcache = "*"
-- pyyaml = "*"

## warehouse-app

**Add to warehouse-django**

amqp = "*"
djangorestframework = "*"
django-markup = "*"
pid = "*"
-- docutils = "*"
pytz = "*"
-- requests = "*"

## warehouse-management

python_version = "3.10"

ansible = "==2.10.7"
boto = "*"
awscli = "*"
"boto3" = "*"
