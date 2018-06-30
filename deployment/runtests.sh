#!/bin/bash

if [[ -z "$DOCKER_HOST" ]]; then
    eval $(docker-machine env default)
fi

#docker-compose up -d beanstalkd ldap

#CWD="$(pwd)"

#cd ../

LDAP_PORT=ldap://docker:10389
IPLANT_NOTIFICATION_SERVICE_QUEUE=dev.notifications.queue
DJANGO_SETTINGS_MODULE=agave_id.settings
IPLANT_MESSAGING_HOST=beanstalkd
AGAVE_AUTH_TYPE=noauth

python manage.py test service
