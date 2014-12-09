#!/bin/bash
# Just like startup.sh, but adds a couple tenants for testing out the multi-tenant mode of the service.
# Note that the settings that ship with this project turn off multi-tenant so in order to test use this
# script you must turn that setting on first and rebuild the agave_id docker image.
#!/bin/bash

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