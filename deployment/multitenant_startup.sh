#!/bin/bash
# Just like startup.sh, but adds a couple tenants for testing out the multi-tenant mode of the service.

fig -f multifig.yml up -d
echo "Waiting for services to start..."
sleep 5
echo "Adding tenants and test users..."
curl -X POST --data ou=tenant1 localhost:8000/ous
curl -X POST --data ou=tenant5 localhost:8000/ous
curl -X POST --data ou=tenantaraport-org localhost:8000/ous
curl -X POST --data "username=jdoe&password=abcde&email=jdoe@test.com" localhost:8000/1/profiles/v2
curl -X POST --data "username=wscarbor&password=abcde&email=wscarbor@vdj.org" localhost:8000/vdj-org/profiles/v2
curl -X POST --data "username=mvaughn&password=abcde&email=mvaughn@aip.org" localhost:8000/araport-org/profiles/v2
echo "agave_id running on port 8000 and ldap running on 10389."
echo "You can now try out the service."
echo "Example: curl localhost:8000/<tenant>/profiles/v2/ to get the users of the tenant."
echo "Stop the services with fig stop"

echo "For the web application you will need a local mail server. You can run a development"
echo "server with:"
echo "python -m smtpd -n -c DebuggingServer 172.17.42.1:1025"