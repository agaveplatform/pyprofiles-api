 #-*- coding: utf-8 -*-
"""
Models for the Agave hosted identity service. LdapUser model borrows heavily
from the django-ldapdb example model.
"""

__author__ = 'jstubbs'

from django.conf import settings
from ldapdb.models.fields import CharField, IntegerField
import ldapdb.models


class LdapUser(ldapdb.models.Model):
    """
    Class for representing an LDAP user entry.
    """
    # LDAP meta-data
    base_dn = 'ou=tenant' + settings.APP_TENANT_ID + ',' + settings.LDAP_BASE_SEARCH_DN
#     object_classes = ['posixAccount', 'shadowAccount', 'inetOrgPerson']
    object_classes = ['inetOrgPerson']

    # inetOrgPerson
    first_name = CharField(db_column='givenName', blank=True)
    last_name = CharField(db_column='sn', blank=True)
    full_name = CharField(db_column='cn', blank=True)
    email = CharField(db_column='mail')
    phone = CharField(db_column='telephoneNumber', blank=True)
    mobile_phone = CharField(db_column='mobile', blank=True)
    nonce = CharField(db_column='employeeNumber', blank=True)
    status = CharField(db_column='employeeType', blank=True)
    create_time = CharField(db_column='createTimestamp', blank=True)

    # posixAccount
    uid = IntegerField(db_column='uidNumber', unique=True, blank=True)
    username = CharField(db_column='uid', primary_key=True)
    password = CharField(db_column='userPassword', blank=True)

    def __str__(self):
        return self.username

    def __unicode__(self):
        return self.full_name


class LdapOU(ldapdb.models.Model):
    """
    Class for representing an LDAP organizational unit.
    """
    # LDAP meta-data
    base_dn = settings.LDAP_BASE_SEARCH_DN
    object_classes = ['organizationalUnit']

    ou = CharField(db_column='ou', blank=True, primary_key=True)

    def __str__(self):
        return self.ou

    def __unicode__(self):
        return self.ou