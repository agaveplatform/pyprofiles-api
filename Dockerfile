# Image: tacc/agave_id

FROM agaveplatform/template_compiler
MAINTAINER Rion Dooley

RUN touch /fooy
RUN apt-get update
RUN apt-get install -y python python-dev python-pip git libldap2-dev libsasl2-dev \
		apache2 apache2-utils libexpat1 ssl-cert libapache2-mod-wsgi lynx ldap-utils

ADD deployment/ldap.conf /etc/ldap/ldap.conf

RUN mkdir -p /code /Users/dooley/agave/api/starters && \
		pip install -U pip
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

EXPOSE 80

CMD /usr/sbin/apache2ctl -D FOREGROUND
