__author__ = 'jstubbs'

import logging
import json
import random
import sys;

import ldap
from django.conf import settings
from django.core.urlresolvers import reverse

from common.error import Error

from agave_id.models import LdapUser

logger = logging.getLogger(__name__)

TENANTS = {'araport-org': {'base_dn':'ou=tenantaraport-org,' + settings.LDAP_BASE_SEARCH_DN},
           'vdj-org': {'base_dn':'ou=tenant5,' + settings.LDAP_BASE_SEARCH_DN},
           'irec': {'base_dn':'ou=tenantirec,' + settings.LDAP_BASE_SEARCH_DN},
           }

def audit_ldap_user(user):
    """
    Basic audits.
    """
    if not user.username or len(user.username) == 0:
        raise Error("Error creating user; username required.")
    if not user.password or len(user.password) == 0:
        raise Error("Error creating user; password required.")
    if not user.email or len(user.email) == 0:
        raise Error("Error creating user; email required.")

def create_ldap_user(username=None,
                       password=None,
                       first_name=None,
                       last_name=None,
                       full_name=None,
                       email=None,
                       phone=None,
                       attrs=None):
    """
    Returns an LdapUser model object from the parameters. Either send an attrs
    dictionary with all attributes (e.g. request.POST), or send individual
    attributes.
    """
    if not attrs:
        attrs = {}
    if type(attrs) == str:
        try:
            attrs = json.loads(attrs)
        except Exception as e:
            raise Error("Invalid payload format")
    u = LdapUser()
    u.username = username or attrs.get('username')
    logger.debug("create_ldap_user using username: " + str(u.username))
    u.password = password or attrs.get('password')
    u.first_name = first_name or attrs.get('first_name')
    u.last_name = last_name or attrs.get('last_name')
    u.full_name = full_name or attrs.get('full_name')
    if not u.full_name:
        if u.first_name and u.last_name:
            u.full_name = u.first_name + " " + u.last_name
        elif u.last_name:
            u.full_name = u.last_name
        elif u.first_name:
            u.full_name = u.first_name
        else:
            u.full_name = u.username
    if not u.last_name:
        u.last_name = u.full_name
    u.email = email or attrs.get('email')
    if phone or attrs.get('phone'):
        u.phone = phone or attrs.get('phone')
    u.status = settings.INACTIVE_STATUS
    u.nonce = str(random.randrange(0, 999999999))
    # u.create_time = str(datetime.datetime.now())
    # u.create_time = time.strftime('%Y %m %d %H %M %S', time.localtime()).replace(" ", "")
    return u

def save_ldap_user(user=None, serializer=None):
    """
    Attempts to save an LdapUser object or a serializer object in the DB and returns error responses
    if LDAP constraints are not met.

    Calling method should pass either an LdapUser object or an LdapUserSerializer object.
    """
    saver_object = user
    if not saver_object:
        if not serializer:
            raise Error("No saver object passed.")
        saver_object = serializer
    try:
        saver_object.save()
    except ldap.ALREADY_EXISTS as e:
        raise Error("username already exists.")
    except ldap.CONSTRAINT_VIOLATION as e:
        logger.debug("constraint violation: " + str(e)+ " DIR: " + str(dir(e)))
        msgs = str(e).split("Active\\n: ")
        logger.debug("msgs:" + str(msgs))
        if len(msgs) == 2:
            msg = msgs[1]
            idx = msg.find('"')
            msg = msg[:idx]
            logger.debug("msg:" + msg + " msgs[0]:" + msgs[0] + " msgs[1]:" + msgs[1] + " idx:" + str(idx))
        else:
            msgs = e.message.get('info').split('ldap.model.message.ModifyRequestImpl')
            if len(msgs) == 2 and len(msgs[1].split(': ')) == 2:
                msg = msgs[1].split(': ')[1]
            else:
                msg = "Password does not meet security requirements or is a previously used password."
        raise Error(msg)

    except Exception as e:
        logger.debug("Error trying to add user. Exception: "+ str(e))
        raise Error("Error trying to add user." + " Msg:" + str(e))
    return None

def get_filter(request):
    """Return filter:value from request query parameters"""
    filters = ['name', 'email', 'first_name', 'last_name', 'full_name', 'status', 'username', ]
    for f in filters:
        if request.GET.get(f):
            if f == 'name':
                return {'full_name': request.GET.get(f)}
            return {f: request.GET.get(f)}
    return None


def get_page_parms(request):
    """ Return limit and offset based on request."""
    limit = request.GET.get('limit', -1)
    try:
        limit = int(limit)
    except ValueError:
        limit = -1
    if limit < -1:
        limit = -1
    offset = request.GET.get('offset', -1)
    try:
        offset = int(offset)
    except ValueError:
        offset = 0
    if offset < 0:
        offset = 0
    return limit, offset


def get_email_message(user):
    """
    Construct activation email message.
    """
    return ("A new Agave account was requested on behalf of this email address." +
            " If this request really came from you, load the following page to " +
            "activate this account: \n"+ settings.EMAIL_BASE_URL + reverse("user_validate") +
            "?username=" + user.username + "&nonce=" + user.nonce)

def populate_context(user, c={}):
    """
    Populate a context dictionary with user attributes.
    """
    c['username'] = user.username
    c['email'] = user.email
    c['first_name'] = user.first_name
    c['last_name'] = user.last_name
    return c

def get_base_dn(tenant):
    """
    Return the base_dn for this tenant
    """
    # see if tenant is in special dictionary defined above:
    if TENANTS.get(tenant):
        return TENANTS.get(tenant).get('base_dn')
    # otherwise, build it in the obvious way:
    else:
        return 'ou=tenant' + str(tenant) + ',' + settings.LDAP_BASE_SEARCH_DN


def multi_tenant_setup(tenant):
    if not tenant:
        raise Error("Tenant-id required.")
    LdapUser.base_dn = get_base_dn(tenant)
