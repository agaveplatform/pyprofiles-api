# Agave Multi-tenant Hosted Identity #

## Overview ##

This project provides a configurable, multi-tenant, ldap backed, identity provider in the form of two Django
applications: a RESTful web service and a self-service sign up web application. This project makes up the
Agave platform's hosted identity offering. It may be of general interest to developers of Django applications but also includes features specific to the Agave platform, such as hooks into the Agave Notifications
service.

## Running from Fig ##
The project ships with a `docker-compose.yml` file for easy deployment locally. The only dependencies are Docker and Docker Compose. Install each and then execute:

```
#!bash

deployment/startup.sh
```

This scipt starts up the service in single-tenant mode. It runs two docker containers - one with the
`user-registration` application and one with an OpenLDAP database. It will also populate the ldap db with an
organizational unit (tenant1) and a test user (username jdoe).

If you would prefer to run the service in multi-tenant mode, execute

```
#!bash

deployment/multitenant_startup.sh
```

instead.