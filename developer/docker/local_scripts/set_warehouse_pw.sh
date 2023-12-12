#!/bin/bash

sed "s/<PASSWORD>/$1/" postgresql_setup.sql > postgresql_setup_customized.sql
sed "s/<PASSWORD>/$1/" conf/django_prod_mgmt.conf > conf/django_prod_mgmt_customized.conf
sed "s/<PASSWORD>/$1/" conf/warehouse_api.conf > conf/warehouse_api_customized.conf
