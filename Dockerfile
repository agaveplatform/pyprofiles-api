# Image: tacc/agave_id

FROM agaveplatform/template_compiler
MAINTAINER Rion Dooley

RUN apt-get update
RUN apt-get install -y python python-dev git libldap2-dev libsasl2-dev curl jq \
		apache2 apache2-utils libexpat1 ssl-cert libapache2-mod-wsgi lynx ldap-utils

ADD deployment/ldap.conf /etc/ldap/ldap.conf

RUN mkdir -p /code && \
		curl -skL https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py   && \
		python2 get-pip.py
ADD requirements.txt /code/
RUN pip install -r /code/requirements.txt

# Manually set up the apache environment variables
ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2
ENV APACHE_LOCK_DIR /var/lock/apache2
ENV APACHE_PID_FILE /var/run/apache2.pid

RUN touch /var/log/apache2/django.log && \
		touch /tmp/django.log && \
		chmod a+w /var/log/apache2/django.log && \
		chmod a+w /tmp/django.log

ADD agave_id /code/agave_id
RUN touch /code/agave_id/agave_id/running_in_docker && \
		chmod o+rw -R /code/agave_id/ && \
		mkdir -p /home/apim/public_keys/

ADD deployment/wsgi.load /etc/apache2/mods-available/
ADD deployment/apache2.conf /etc/apache2/sites-enabled/000-default.conf
ADD deployment/apim_default.pub  /home/apim/public_keys/apim_default.pub

ENV DJANGO_SETTINGS_MODULE agave_id.settings

EXPOSE 80
#WORKDIR /code/agave_id/
#CMD gunicorn -w 4 -b :80 agave_id.wsgi
CMD /usr/sbin/apache2ctl -D FOREGROUND
