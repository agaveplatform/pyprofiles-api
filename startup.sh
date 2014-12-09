#!/bin/bash

fig up -d
echo "Waiting for services to start..."
sleep 5
echo "Adding tenant1 ou and jdoe user..."
curl -X POST --data ou=tenant1 localhost:8000/ous
curl -X POST --data "username=jdoe&password=abcde&email=jdoe@test.com" localhost:8000/users
echo "agave_id running on port 8000 and ldap running on 10389."
echo "You can now try out the service."
echo "Example: curl localhost:8000/users to get all the users."
echo "Stop the services with fig stop"