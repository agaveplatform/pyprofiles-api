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
    # base_dn = 'ou=tenant' + settings.APP_TENANT_ID + ',' + settings.LDAP_BASE_SEARCH_DN
    base_dn = unicode(settings.LDAP_BASE_SEARCH_DN)
    object_classes = [u'inetOrgPerson']

    # inetOrgPerson
    first_name = CharField(db_column=u'givenName', blank=True)
    last_name = CharField(db_column=u'sn', blank=True)
    full_name = CharField(db_column=u'cn', blank=True)
    email = CharField(db_column=u'mail')
    phone = CharField(db_column=u'telephoneNumber', blank=True)
    mobile_phone = CharField(db_column=u'mobile', blank=True)
    nonce = CharField(db_column=u'employeeNumber', blank=True)
    status = CharField(db_column=u'employeeType', blank=True)
    create_time = CharField(db_column=u'createTimestamp', blank=True)

    # posixAccount
    uid = IntegerField(db_column=u'uidNumber', unique=True, blank=True)
    username = CharField(db_column=u'uid', primary_key=True)
    password = CharField(db_column=u'userPassword', blank=True)

    # def __str__(self):
    #     return self.username

    # def __unicode__(self):
    #     return self.full_name


class LdapOU(ldapdb.models.Model):
    """
    Class for representing an LDAP organizational unit.
    """
    # LDAP meta-data
    # this ONLY works in dev (which is the way it should be). Note that base_dn = settings.LDAP_BASE_SEARCH_DN does
    # NOT work because base_dn = settings.LDAP_BASE_SEARCH_DN now contains the ou!"
    base_dn = u"dc=agaveapi"
    object_classes = [u'organizationalUnit']

    ou = CharField(db_column=u'ou', blank=True, primary_key=True)

    def __str__(self):
        return self.ou

    def __unicode__(self):
        return self.ou