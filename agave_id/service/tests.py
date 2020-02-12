from __future__ import unicode_literals
#
# Tests for the agave_id web service. To run these tests:
# 1, start up the containers using the startup.sh script (this requires docker and docker-compose)
# 2. activate the virtualenv with the requirements installed (this is because the test suite will run
# on the host, not in the container).
# 3. Execute:
#       python manage.py test service
#
# NOTE: The test suite tests the mode of the service given by the current settings: if
# MULTI_TENANT=False, the test suite will exercise the service in single-tenant mode. Otherwise,
# it will test the service in multi-tenant mode.


import os
import sys
APP_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),'..')
for idx, p in enumerate(sys.path):
    if p == APP_DIR:
        sys.path.pop(idx)

sys.path.append(os.path.abspath(os.path.join(APP_DIR,'..')))

import base64
import ldap
import requests
import logging

from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase

from service.models import LdapUser
from service.util import create_ldap_user, save_ldap_user


logger = logging.getLogger(__name__)

APP_BASE = "http://localhost:8000/"
APIM_BASE = "https://agave-am17-dev.tacc.utexas.edu/"

if settings.MULTI_TENANT:
    APP_BASE = APP_BASE + '1/'

class Error(Exception):
    def __init__(self, message=None):
        self.message = message
        if message:
            logger.error("Error raised:" + message)

class LdapUserTests(APITestCase):
    """
    Basic CRUD tests for LdapUser objects
    """

    def setUp(self):
        try:
            user = LdapUser.objects.get(username="jdoe123")
            user.delete()
        except:
            pass
        try:
            user = LdapUser.objects.get(username="jdoe12345")
            user.delete()
        except Exception as e:
            pass
            # print "Exception deleting user: ", str(e)
            # users = LdapUser.objects.all()
            # for user in users:
            #     print user.username
        try:
            user = create_ldap_user(username=u"jdoe12345", password=u"abcde", email=u"jdoe12345@test.com")
            save_ldap_user(user=user)
        except Exception as e:
            raise Error("Unable to set up test db; message: " + str(e.message))
        # insert a JWT
        self.extra = {}
        if settings.CHECK_JWT:
            with open('usersApp/sample_jwt.txt', 'r') as f:
                jwt = f.read().replace('\n', '')
            self.extra = {settings.JWT_HEADER: jwt}

    def tearDown(self):
        try:
            user = LdapUser.objects.get(username="jdoe123")
            user.delete()
        except:
            pass
        try:
            user = LdapUser.objects.get(username="jdoe12345")
            user.delete()
        except:
            pass


    def test_user_create(self):
        """
        Create a user
        """
        url = APP_BASE + "users/"
        data = {"username":"jdoe123", "password":"abcde", "email":"jdoe123@test.com"}
        r = self.client.post(url, data, format="json", **self.extra)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.data.get("status"), "success")
        self.assertEqual(r.data.get("result").get("username"), "jdoe123")

    def test_user_update_pass(self):
        url = APP_BASE + "users/jdoe12345/"
        data = {"password":"abcdefg", "email":"jdoe12345@test.com"}
        r = self.client.put(url, data, format="json", **self.extra)
        self.assertEqual(r.status_code, 201, "Error updating user: " + str(r.status_code)
                                             + " response: " + r.content)
        self.assertEqual(r.data.get("status"), "success")
        self.assertEqual(r.data.get("result").get("username"), "jdoe12345")

    def test_user_update_pass_special_chars(self):
        url = APP_BASE + "users/jdoe12345/"
        data = {"password": "~!@#$%^&*()_+=-`{}|:<>?[]\;',./", "email":"jdoe12345@test.com"}
        r = self.client.put(url, data, format="json", **self.extra)
        self.assertEqual(r.status_code, 201, "Error updating user: " + str(r.status_code)
                                             + " response: " + r.content)
        self.assertEqual(r.data.get("status"), "success")
        self.assertEqual(r.data.get("result").get("username"), "jdoe12345")

    def test_user_update_pass_five_spaces(self):
        url = APP_BASE + "users/jdoe12345/"
        data = {"password": "     ", "email":"jdoe12345@test.com"}
        r = self.client.put(url, data, format="json", **self.extra)
        self.assertEqual(r.status_code, 201, "Error updating user: " + str(r.status_code)
                                             + " response: " + r.content)
        self.assertEqual(r.data.get("status"), "success")
        self.assertEqual(r.data.get("result").get("username"), "jdoe12345")


    def test_user_update_pass_not_too_short(self):
        url = APP_BASE + "users/jdoe12345/"
        data = {"password":"abcd", "email":"jdoe12345@test.com"}
        r = self.client.put(url, data, format="json", **self.extra)
        self.assertEqual(r.status_code, 201, "Wrong status code: " + str(r.status_code)
                                             + " response: " + r.content)
        self.assertEqual(r.data.get("status"), "success")
        self.assertEqual(r.data.get("result").get("username"), "jdoe12345")

    def test_user_update_pass_prev(self):
        url = APP_BASE + "users/jdoe12345/"
        data = {"password":"abcdef", "email":"jdoe12345@test.com"}
        r = self.client.put(url, data, format="json", **self.extra)
        data = {"password":"abcde", "email":"jdoe12345@test.com"}
        r = self.client.put(url, data, format="json", **self.extra)
        self.assertEqual(r.status_code, 201, "Wrong status code: " + str(r.status_code)
                                             + " response: " + r.content)
        self.assertEqual(r.data.get("status"), "success")
        self.assertEqual(r.data.get("result").get("username"), "jdoe12345")

    def test_user_update_pass_prev5(self):
        url = APP_BASE + "users/jdoe12345/"
        data = {"password":"abcdef", "email":"jdoe12345@test.com"}
        r = self.client.put(url, data, format="json", **self.extra)
        data = {"password":"abcdefg", "email":"jdoe12345@test.com"}
        r = self.client.put(url, data, format="json", **self.extra)
        data = {"password":"abcdefh", "email":"jdoe12345@test.com"}
        r = self.client.put(url, data, format="json", **self.extra)
        data = {"password":"abcdefhi", "email":"jdoe12345@test.com"}
        r = self.client.put(url, data, format="json", **self.extra)
        # should not be able to use a password in the previous 5 passwords (initial + 4 updates)
        data = {"password":"abcde", "email":"jdoe12345@test.com"}
        r = self.client.put(url, data, format="json", **self.extra)
        self.assertEqual(r.status_code, 201, "Wrong status code: " + str(r.status_code)
                                             + " response: " + r.content)
        self.assertEqual(r.data.get("status"), "success")
        self.assertEqual(r.data.get("result").get("username"), "jdoe12345")

    def test_user_update_pass_prev6_ok(self):
        url = APP_BASE + "users/jdoe12345/"
        data = {"password":"abcdef", "email":"jdoe12345@test.com"}
        r = self.client.put(url, data, format="json", **self.extra)
        data = {"password":"abcdefg", "email":"jdoe12345@test.com"}
        r = self.client.put(url, data, format="json", **self.extra)
        data = {"password":"abcdefh", "email":"jdoe12345@test.com"}
        r = self.client.put(url, data, format="json", **self.extra)
        data = {"password":"abcdefhi", "email":"jdoe12345@test.com"}
        r = self.client.put(url, data, format="json", **self.extra)
        data = {"password":"abcdefhij", "email":"jdoe12345@test.com"}
        r = self.client.put(url, data, format="json", **self.extra)

        # after 5 updates, should be able to use the original password
        data = {"password":"abcde", "email":"jdoe12345@test.com"}
        r = self.client.put(url, data, format="json", **self.extra)
        self.assertEqual(r.status_code, 201, "Error updating user: " + str(r.status_code)
                                             + " response: " + r.content)
        self.assertEqual(r.data.get("status"), "success")
        self.assertEqual(r.data.get("result").get("username"), "jdoe12345")

    def test_user_update_pass_username_1(self):
        url = APP_BASE + "users/jdoe12345/"
        # passwords can now contain the username:
        data = {"password":"zzjdoe", "email":"jdoe12345@test.com"}
        r = self.client.put(url, data, format="json", **self.extra)
        self.assertEqual(r.status_code, 201, "Wrong status code: " + str(r.status_code)
                                             + " response: " + r.content)
        self.assertEqual(r.data.get("status"), "success")
        self.assertEqual(r.data.get("result").get("username"), "jdoe12345")

    def test_user_update_pass_username_2(self):
        url = APP_BASE + "users/jdoe12345/"
        # passwords can contain username with different case:
        data = {"password":"zzJDOE", "email":"jdoe12345@test.com"}
        r = self.client.put(url, data, format="json", **self.extra)
        self.assertEqual(r.data.get("status"), "success")
        self.assertEqual(r.data.get("result").get("username"), "jdoe12345")

    def test_user_update_pass_username_ok1(self):
        url = APP_BASE + "users/jdoe12345/"
        # passwords can contain the first 3 or fewer characters:
        data = {"password":"zzjdo", "email":"jdoe12345@test.com"}
        r = self.client.put(url, data, format="json", **self.extra)
        self.assertEqual(r.status_code, 201, "Wrong status code: " + str(r.status_code)
                                             + " response: " + r.content)
        self.assertEqual(r.data.get("status"), "success")
        # print r.data.get("message")
        self.assertEqual(r.data.get("result").get("username"), "jdoe12345")

    def test_user_update_pass_username_ok2(self):
        url = APP_BASE + "users/jdoe12345/"
        # passwords can sometimes contain username tokens of any length if they dont
        # start at the first character:
        data = {"password":"zzdoe12345zz12345zzdoedoedoezzjdo", "email":"jdoe12345@test.com"}
        r = self.client.put(url, data, format="json", **self.extra)
        self.assertEqual(r.status_code, 201, "Wrong status code: " + str(r.status_code)
                                             + " response: " + r.content)
        self.assertEqual(r.data.get("status"), "success")
        # print r.data.get("message")
        self.assertEqual(r.data.get("result").get("username"), "jdoe12345")


    def test_list_users(self):
        url = APP_BASE + "users/"
        r = self.client.get(url, format="json", **self.extra)
        self.assertEqual(r.status_code, 200, "Wrong status code: " + str(r.status_code)
                                             + " response: " + r.content)
        self.assertEqual(r.data.get("status"), "success")
        result = r.data.get("result")
        found = False
        for user in result:
            assert not 'password' in user
            if user.get("username") == "jdoe12345":
                found = True
        self.assertEqual(found, True)

    def test_get_user_details(self):
        url = APP_BASE + "users/jdoe12345/"
        r = self.client.get(url, format="json", **self.extra)
        self.assertEqual(r.status_code, 200, "Wrong status code: " + str(r.status_code)
                                             + " response: " + r.content)
        self.assertEqual(r.data.get("status"), "success")
        username = r.data.get("result").get("username")
        assert not 'password' in r.data.get("result")
        self.assertEqual(username, "jdoe12345")

    def test_get_me_user_details(self):
        # This test will not pass if the service isn't using the JWT from apim.
        if not settings.CHECK_JWT:
            logger.warn("Did not test the 'me' feature since CHECK_JWT was False.")
            return
        url = APP_BASE + "users/me/"
        r = self.client.get(url, format="json", **self.extra)
        self.assertEqual(r.status_code, 200, "Wrong status code: " + str(r.status_code)
                                             + " response: " + r.content)
        self.assertEqual(r.data.get("status"), "success")
        username = r.data.get("result").get("username")
        assert not 'password' in r.data.get("result")
        self.assertEqual(username, "jstubbs")


def http_auth(username, password):
    credentials = base64.encodestring('%s:%s' % (username, password)).strip()
    auth_string = 'Basic %s' % credentials
    return auth_string
