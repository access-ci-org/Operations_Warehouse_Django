# Service Facing Information Sharing Platform - Developer Setup


Instructions for setting up a development environment.

## Development Tools

### Mac editors

- [Development Tools](https://developer.apple.com/develop/) ([download](https://developer.apple.com/download/))
- [Command Line Tools](https://developer.apple.com/download/more/)

or:

- [VS Code](https://code.visualstudio.com)

### Windows editors

Install Windows Subsystem for Linux:

- [About](https://learn.microsoft.com/en-us/windows/wsl/about)

## Runtime Tools

Docker from any provider.

### Mac runtime

Install https://rancherdesktop.io
Place in ~/Library/Application Support/rancher-desktop/lima/_config/override.yaml:

provision:
- mode: system
  script: |
    #!/bin/sh
    cat <<'EOF' > /etc/security/limits.d/rancher-desktop.conf
    * soft     nofile         82920
    * hard     nofile         82920
    EOF
    sysctl -w vm.max_map_count=262144

### Windows runtime

TBD

## Checkout Warehouse

From https://github.com/access-ci-org/Operations_Warehouse_Django

## PostgreSQL database

From: Operations_Warehouse_Django/developer/docker

1) Edit postgresql.yml and set POSTGRES_PASSWORD
2) docker-compose -f postgresql.yml up -d
3) psql -U opsdba -h localhost -p 5432 postgres
   postgres=# \i postgresql_setup.sql
   
3) psql -U info_django -h localhost -p 5432 warehouse2
   postgres=# \i backup.dump
   
## OpenSearch service

From: Operations_Warehouse_Django/developer/docker

1) docker-compose -f opensearch.yml up -d
2) Using OpenSearch Dashboard
2.1) Create internal user: resource-v4-index/<password>

# Notes

opensearch.yml came from https://opensearch.org/samples/docker-compose.yml


