# Agave Multi-tenant Hosted Identity #

## Overview ##

This project provides a configurable, multi-tenant, ldap backed, identity provider in the form of two Django
applications: a RESTful web service and a self-service sign up web application. This is the project behind
Agave's hosted identity offering. It may be of general interest to developers of Django applications but also
includes features specific to the Agave platform, such as hooks into the Agave Notifications service.

## Running from Fig ##
The project comes with a fig.yml file for easy deployment locally. The only dependencies are
docker and Fig. Install each for your platform and then execute:

./startup.sh

This will start up two docker containers - one with the agave_id application and one with an
openldap db. It will also populate the ldap db with an organizational unit (tenant1) and a test user
(username jdoe).