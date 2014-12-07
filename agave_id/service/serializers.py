__author__ = 'jstubbs'

import random
from django.conf import settings
from rest_framework import serializers

from agave_id.models import LdapUser


class LdapUserSerializer(serializers.ModelSerializer):

#     username = serializers.Field()

    class Meta:
        model = LdapUser
        fields = ('first_name', 'last_name', 'full_name', 'email', 'phone', 'mobile_phone', 'status', 'create_time',
                  'uid', 'username', 'password')
        depth = 1

    def validate(self, attrs):
        """
        Handles derived attributes and cross-field validation,
        A valid uid will be used for the full name if the names fields are not specified.
        """
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
            
        # users added through REST API are automatically active:
        attrs['status'] = settings.ACTIVE_STATUS
        attrs['nonce'] = str(random.randrange(0, 999999999))
        # attrs['create_time'] = str(datetime.datetime.now())
        # attrs['create_time'] = time.strftime('%Y %m %d %H %M %S', time.localtime()).replace(" ", "") + "Z"
        return attrs

    def restore_object(self, attrs, instance=None):
        """
        Create or update a new LdapUser instance, given a dictionary
        of deserialized field values.

        Note that if we don't define this method, then deserializing
        data will simply return a dictionary of items.
        """
        if instance:
            # Update existing instance
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
            return instance

        # Create new instance
        return LdapUser(**attrs)