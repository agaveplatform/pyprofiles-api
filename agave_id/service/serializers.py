from __future__ import unicode_literals

__author__ = 'jstubbs'

import logging
import random
from datetime import datetime
from django.conf import settings
from rest_framework import serializers

from service.models import LdapUser
from pycommon.notifications import build_profile_uuid
# Get an instance of a logger
logger = logging.getLogger(__name__)

class LdapUserSerializer(serializers.ModelSerializer):

#     username = serializers.Field()

    class Meta:
        model = LdapUser
        fields = ('first_name', 'last_name', 'full_name', 'email', 'phone', 'mobile_phone', 'nonce', 'status', 'create_time',
                  'uid', 'username', 'password', 'organization_name')
        depth = 1

    def validate(self, attrs):
        """
        Handles derived attributes and cross-field validation,
        A valid uid will be used for the full name if the names fields are not specified.
        """
        logger.debug("Top of LdapUserSerializer.validate.")
        if not attrs.get('full_name'):
            if attrs.get('first_name') and attrs.get('last_name'):
                attrs['full_name'] = attrs.get('first_name') + " " + attrs.get('last_name')
            elif attrs.get("last_name"):
                attrs['full_name'] = attrs.get('last_name')
            elif attrs.get('first_name'):
                attrs['full_name'] = attrs.get('first_name')
            else:
                attrs['full_name'] = attrs.get('username')
        if not attrs.get('last_name'):
            attrs['last_name'] = attrs.get('full_name')

        # users added through REST API are automatically active unless status is specified:
        if attrs.get('status'):
            attrs['status'] = attrs.get('status')
        else:
            attrs['status'] = settings.ACTIVE_STATUS

        attrs['nonce'] = str(random.randrange(0, 999999999))
        # attrs['create_time'] = time.strftime('%Y %m %d %H %M %S', time.localtime()).replace(" ", "") + "Z"
        # attrs['create_time'] = time.strftime('%Y %m %d', time.localtime()).replace(" ", "")
        # logger.debug("create_time: {}".format(attrs['create_time']))
        logger.debug("returning from LdapUserSerializer.validate. attrs: {}".format(attrs))
        return attrs

    def validate_username(self, value):
        """
        Check that the blog post is about Django.
        """
        if '@' in value:
            raise serializers.ValidationError("Email addresses and usernames with @ symbols are not allowed.")
        if value == 'me':
            raise serializers.ValidationError("me is a reserved and cannot be used for a username.")
        return value

    def create(self, attrs):
        return LdapUser(**attrs)

    def update(self, instance, attrs):
        instance.first_name = attrs.get('first_name', instance.first_name)
        instance.last_name = attrs.get('last_name', instance.last_name)
        instance.email = attrs.get('email', instance.email)
        instance.phone = attrs.get('phone', instance.phone)
        instance.mobile_phone = attrs.get('mobile_phone', instance.mobile_phone)
        instance.nonce = attrs.get('nonce', instance.nonce)
        instance.status = attrs.get('status', instance.status)
        instance.create_time = attrs.get('create_time', instance.create_time)
        instance.uid = attrs.get('uid', instance.uid)
        instance.username = attrs.get('username', instance.username)
        instance.password = attrs.get('password', instance.password)
        instance.full_name = attrs.get('full_name', instance.full_name)
        instance.organization_name = attrs.get('organization_name', instance.organization_name)
        return instance

    def to_representation(self, obj):
        ret = super(LdapUserSerializer, self).to_representation(obj)
        # Remove password for obvious reasons
        ret.pop('password', None)
        # Remove nonce from string so others cannot active accounts via the activation page
        ret.pop('nonce', None)
        # formate create_time field to a proper ISO8601 formatted date time string
        formatted_create_time = datetime.strptime(ret['create_time'], '%Y%m%d%H%M%SZ').strftime("%Y-%m-%dT%H:%M:%SZ")
        ret['create_time'] = formatted_create_time
        ret['uuid'] = build_profile_uuid(obj.username)
        self_href = "{}/profiles/v2/{}".format(settings.APP_BASE, obj.username)
        ret['_links'] = { 'self': { 'href':  self_href } }
        return ret