__author__ = 'jstubbs'

import logging

from django import db
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from common.auth import authenticated
from common.error import Error
from common.responses import success_dict, error_dict
from common.notifications import create_notification
from service.models import LdapUser

# from service.models import LdapUser
from service import ou
from service import util

from serializers import LdapUserSerializer

# Get an instance of a logger
print("Getting a logger for: {}".format(__name__))
logger = logging.getLogger(__name__)


class OUs(APIView):
    def perform_authentication(self, request):
        # Overriding the authentication performed by Django REST Framework since we are handling it ourselves
        pass

    @authenticated
    def get(self, request, format=None):
        """
        List OUs in the LDAP db
        """
        logger.debug("top of GET /ous")
        if settings.CHECK_JWT and settings.CHECK_USER_ADMIN_ROLE and not request.service_admin:
            return Response(error_dict(msg="Access denied."), status=status.HTTP_401_UNAUTHORIZED)
        try:
            logger.debug("Getting ous...")
            ous = ou.get_ous()
            # ous = []
        except Exception as e:
            logger.error("Got exception retrieving the list of ous. Exception: {}".format(e))
            return Response(error_dict(msg="Error retrieving OUs: {}".format(e)))
        finally:
            db.close_old_connections()
            logger.debug("old connections closed.")
        return Response(success_dict(msg="Organizational Units retrieved successfully.", result=ous.values()))


    @authenticated
    def post(self, request, format=None):
        """
        Create an OU.

        ou -- (REQUIRED) The organizational unit to create.
        """
        logger.debug("top of POST /ous")
        if settings.READ_ONLY:
            logger.debug("service set to READ_ONLY. Returning 400.")
            return Response(error_dict(msg="Read-only service."), status=status.HTTP_400_BAD_REQUEST)
        if settings.CHECK_JWT and settings.CHECK_USER_ADMIN_ROLE and not request.service_admin:
            logger.debug("missing required role. Returning 401.")
            return Response(error_dict(msg="Access denied."), status=status.HTTP_401_UNAUTHORIZED)
        try:
            ou.create_ou(request.POST.get('ou'))
        except Exception as e:
            logger.error("Got exception trying to create OU. e: {}".format(e))
            return Response(error_dict(msg="Error trying to create OU: " + str(e)))
        finally:
            db.close_old_connections()
            logger.debug("old connections closed.")
        return Response(success_dict(msg="OU created successfully."))


class Users(APIView):

    def perform_authentication(self, request):
        # Overriding the authentication performed by Django REST Framework since we are handling it ourselves
        pass

    @authenticated
    def get(self, request, tenant=None, format=None):
        """
        List all users.
        """
        logger.debug("top of GET /users")
        if settings.MULTI_TENANT:
            util.multi_tenant_setup(tenant)
        filter_dict = util.get_filter(request)
        try:
            if filter_dict:
                users = LdapUser.objects.filter(**filter_dict)
            else:
                users = LdapUser.objects.all()
        except Exception as e:
            logger.error("Got exception trying to retrieve users; e: {}".format(e))
            return Response(error_dict(msg="Error retrieving users: " + str(e)))
        limit, offset = util.get_page_parms(request)
        if limit > 0:
            users = users[offset: offset+limit]
        serializer = LdapUserSerializer(users, many=True)
        db.close_old_connections()
        return Response(success_dict(msg="Users retrieved successfully.", result=serializer.data, query_dict=request.GET))

    @authenticated
    def post(self, request, tenant=None, format=None):
        """
        Create a new user.

        username -- (REQUIRED) The username for the account
        password -- (REQUIRED) The password for the account
        email -- (REQUIRED) email address
        first_name -- first name
        last_name -- last name
        phone  -- phone number
        mobile_phone  -- mobile phone number
        status -- user status
        """
        logger.debug("top of POST /users")
        if settings.READ_ONLY:
            return Response(error_dict(msg="Read-only service.", query_dict=request.GET), status=status.HTTP_400_BAD_REQUEST)
        if settings.MULTI_TENANT:
            util.multi_tenant_setup(tenant)
        if settings.CHECK_JWT and settings.CHECK_USER_ADMIN_ROLE and not request.service_admin:
            return Response(error_dict(msg="Access denied.", query_dict=request.GET), status=status.HTTP_401_UNAUTHORIZED)
        serializer = LdapUserSerializer(data=request.data)
        # password only required on POST
        if not request.data.get("password"):
            serializer.errors['password'] = ["This field is required."]
        if request.data.get('username') == "me":
            serializer.errors['username'] = ["me is a reserved and cannot be used for a username."]
        if serializer.is_valid():
            print("serializer.is_valid: {}".format(serializer.is_valid()))
            try:
                util.save_ldap_user(serializer=serializer)
                logger.info("user {} saved in db".format(request.data.get('username')))
            except Error as e:
                logger.error("got exception trying to save user: {}".format(e))
                return Response(error_dict(msg=e.message, query_dict=request.GET), status.HTTP_400_BAD_REQUEST)
            finally:
                db.close_old_connections()
            if settings.CREATE_NOTIFICATIONS:
                logger.debug("creating a notification for new user: {}".format(request.data.get('username')))
                create_notification(request.data.get('username'), "CREATED", "jstubbs")
            return Response(success_dict(msg="User created successfully.",
                                         result=serializer.data, query_dict=request.GET),
                            status=status.HTTP_201_CREATED)
        return Response(error_dict(result=serializer.errors,
                                   msg="Error creating user.", query_dict=request.GET), status.HTTP_400_BAD_REQUEST)

class UserDetails(APIView):
    def perform_authentication(self, request):
        # Overriding the authentication performed by Django REST Framework since we are handling it ourselves
        pass

    @authenticated
    def get(self, request, username, tenant=None, format=None):
        """
        Retrieve user details
        """
        logger.debug("top of GET /users/{}".format(username))
        if settings.MULTI_TENANT:
            util.multi_tenant_setup(tenant)
        if request.username and username == "me":
            username = request.username
        try:
            user = LdapUser.objects.get(username=username)
        except Exception as e:
            logger.error("Got exception trying to retrieve user details. user: {}; e: {}".format(username, e))
            return Response(error_dict(msg="Error retrieving user details.", query_dict=request.GET), status=status.HTTP_404_NOT_FOUND)
        finally:
            db.close_old_connections()
        serializer = LdapUserSerializer(user)

        return Response(success_dict(result=serializer.data, msg="User details retrieved successfully.", query_dict=request.GET))

    @authenticated
    def put(self, request, username, tenant=None, format=None):
        """
        Update user details

        email -- (REQUIRED) email address
        password -- The password for the account; should only be passed when updating the password.
        first_name -- first name
        last_name -- last name
        phone  -- phone number
        mobile_phone  -- mobile phone number
        status -- user status

        """
        logger.debug("top of PUT /users/{}".format(username))
        if settings.READ_ONLY:
            return Response(error_dict(msg="Read-only service.", query_dict=request.GET), status=status.HTTP_400_BAD_REQUEST)
        if settings.MULTI_TENANT:
            util.multi_tenant_setup(tenant)
        if settings.CHECK_JWT and settings.CHECK_USER_ADMIN_ROLE and not request.service_admin:
            if not username == request.username:
                if settings.CREATE_NOTIFICATIONS:
                    create_notification(username, "UPDATED", "jstubbs")
                return Response(error_dict(msg="Access denied.", query_dict=request.GET), status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = LdapUser.objects.get(username=username)
        except Exception as e:
            logger.error("Got exception trying to retrieve user details in PUT. user: {}; e: {}".format(username, e))
            db.close_old_connections()
            return Response(error_dict(msg="Error retrieving user details: account not found.", query_dict=request.GET),
                            status=status.HTTP_404_NOT_FOUND)
        # we need to add username to the dictionary for serialization, but request.data is
        # immutable for PUT requests from some clients (e.g.curl)
        data = request.data.copy()
        data['username'] = user.username
        serializer = LdapUserSerializer(user, data=data)
        if serializer.is_valid():
            try:
                util.save_ldap_user(serializer=serializer)
            except Error as e:
                logger.error("Got exception trying to update user details in PUT. user: {}; e: {}; data: {}".format(username, e, data))
                return Response(error_dict(msg=e.message, query_dict=request.GET), status.HTTP_400_BAD_REQUEST)
            finally:
                db.close_old_connections()
            return Response(success_dict(result=serializer.data,
                                         msg="User updated successfully.", query_dict=request.GET),
                            status=status.HTTP_201_CREATED)
        return Response(error_dict(msg="Error updating user.",
                                   result=serializer.errors, query_dict=request.GET),
                        status=status.HTTP_400_BAD_REQUEST)

    @authenticated
    def delete(self, request, username, tenant=None, format="json"):
        """
        Delete user
        """
        logger.debug("top of DELETE /users/{}".format(username))
        if settings.READ_ONLY:
            return Response(error_dict(msg="Read-only service.", query_dict=request.GET), status=status.HTTP_400_BAD_REQUEST)
        if settings.MULTI_TENANT:
            util.multi_tenant_setup(tenant)
        if settings.CHECK_JWT and settings.CHECK_USER_ADMIN_ROLE and not request.service_admin:
            if not username == request.username:
                return Response(error_dict(msg="Access denied.", query_dict=request.GET), status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = LdapUser.objects.get(username=username)
        except Exception as e:
            logger.error("Got exception trying to delete user. user: {}; e: {}".format(username, e))
            db.close_old_connections()
            return Response(error_dict(msg="Error deleting user: account not found.", query_dict=request.GET),
                            status=status.HTTP_404_NOT_FOUND)
        user.delete()
        db.close_old_connections()
        if settings.CREATE_NOTIFICATIONS:
            create_notification(username, "DELETED", "jstubbs")
        return Response(success_dict(msg="User deleted successfully.", query_dict=request.GET))
