#!/bin/bash
export WORKON_HOME=/soft/python-pipenv
PYTHON_VERSION=3.10
PYTHON_BINARY=python${PYTHON_VERSION}
PYTHON_BASE=/Library/Frameworks/Python.framework/Versions/${PYTHON_VERSION}
PYTHON_ROOT=/soft/warehouse-2.0/python
source ${PYTHON_ROOT}/bin/activate
export PYTHONPATH=/soft/warehouse-2.0/PROD/
export DJANGO_SETTINGS_MODULE=Operations_Warehouse_Django.settings
#export DJANGO_CONF=/soft/warehouse-2.0/conf/django_dev_mgmt.conf
export APP_CONFIG=/soft/warehouse-2.0/conf/django_dev_mgmt.conf
cd ${PYTHONPATH}
${PYTHON_BINARY} ~/update_badge_resources.py "$@"

