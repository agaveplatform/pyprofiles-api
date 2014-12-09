FROM ubuntu
MAINTAINER Joe Stubbs

RUN apt-get update
RUN apt-get install -y python python-dev python-pip git
RUN apt-get install -y libldap2-dev libsasl2-dev

RUN mkdir /code
ADD requirements.txt /code/
RUN pip install -r /code/requirements.txt

ADD agave_id /code/agave_id/agave_id