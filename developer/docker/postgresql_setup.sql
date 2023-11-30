UPDATE pg_database SET datcollate='en_US.UTF-8', datctype='en_US.UTF-8';

CREATE ROLE warehouse_owner WITH NOSUPERUSER INHERIT NOCREATEROLE NOCREATEDB LOGIN NOREPLICATION ENCRYPTED PASSWORD '<PASSWORD>';
-- Or whomever the postgresl superuser is
GRANT warehouse_owner TO opsdba;

CREATE DATABASE warehouse2 WITH OWNER warehouse_owner encoding ‘UTF8’ LC_COLLATE 'en_US.UTF-8' LC_CTYPE 'en_US.UTF-8';
CREATE ROLE info_django WITH NOSUPERUSER INHERIT NOCREATEROLE NOCREATEDB LOGIN NOREPLICATION ENCRYPTED PASSWORD '<PASSWORD>';

-- Or whomever the postgresl superuser is
GRANT info_django TO opsdba;

\c warehouse2

CREATE SCHEMA info AUTHORIZATION info_django;
ALTER ROLE info_django SET search_path TO info;
