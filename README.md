# Agave Multi-tenant Hosted Identity #

## Overview ##

This project provides a configurable, multi-tenant, ldap backed, identity provider in the form of two Django
applications: a RESTful web service and a self-service sign up web application. This project makes up the
Agave platform's hosted identity offering. It may be of general interest to developers of Django applications but
also includes features specific to the Agave platform, such as hooks into the Agave Notifications
service.

## Running from Docker-compose ##
The project ships with a docker-compose.yml file for easy deployment locally. The only dependencies are
docker and docker-compose. Install each and then, from within the deployment directory, execute:

```
#!bash

$ docker-compose up -d
```

At this point the API as well as an LDAP database should be running within two docker containers. Create
an OU (orgnaizational unit) by making an API call:

```
$ curl -d "ou=tenant1" localhost:8000/ous
```

The response should be something like:

```
{
   "status":"success",
   "message":"OU created successfully.",
   "version":"2.0.0-SNAPSHOT-rc3fad",
   "result":{}
}
```

We can now create and list users in the new OU using the API. For example:

```
$ curl -d "username=test&password=abcd123&email=test@test.com" localhost:8000/users

{
   "status":"success",
   "message":"User created successfully.",
   "version":"2.0.0-SNAPSHOT-rc3fad",
   "result":{
      "first_name":"",
      "last_name":"test",
      "full_name":"test",
      "email":"test@test.com",
      "phone":"",
      "mobile_phone":"",
      "status":"Active",
      "uid":null,
      "username":"test"
   }
}