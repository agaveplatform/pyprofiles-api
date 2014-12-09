__author__ = 'jstubbs'

import logging

from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from common.auth import authenticated
from common.error import Error
from common.responses import success_dict, error_dict
from common.notifications import create_notification
from agave_id.models import LdapUser

# from service.models import LdapUser
from agave_id.service import ou
from agave_id.service import util

from serializers import LdapUserSerializer

# Get an instance of a logger
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
        if settings.CHECK_JWT and settings.CHECK_USER_ADMIN_ROLE and not request.wso2_user_admin:
            return Response(error_dict(msg="Access denied."), status=status.HTTP_401_UNAUTHORIZED)
        try:
            ous = ou.get_ous()
        except Exception as e:
            return Response(error_dict(msg="Error retrieving OUs: " + str(e)))
        # import pdb;pdb.set_trace()
        return Response(success_dict(msg="Organizational Units retrieved successfully.", result=ous.values()))

    @authenticated
    def post(self, request, format=None):
        """
        Create an OU.

        ou -- (REQUIRED) The organizational unit to create.
        """
        if settings.CHECK_JWT and settings.CHECK_USER_ADMIN_ROLE and not request.wso2_user_admin:
            return Response(error_dict(msg="Access denied."), status=status.HTTP_401_UNAUTHORIZED)
        try:
            ou.create_ou(request.POST.get('ou'))
        except Exception as e:
            return Response(error_dict(msg="Error trying to create OU: " + str(e)))
        return Response(success_dict(msg="OU created successfully."))


class Users(APIView):

    def perform_authentication(self, request):
        # Overriding the authentication performed by Django REST Framework since we are handling it ourselves
        pass

    @authenticated
    def get(self, request, format=None):
        """
        List all users.
        """
        users = LdapUser.objects.all()
        serializer = LdapUserSerializer(users, many=True)
        for user in serializer.data:
            # remove password from data:
            user.pop('password', None)
            # remove unused uid field as well:
            user.pop('uid', None)
        return Response(success_dict(msg="Users retrieved successfully.", result=serializer.data))

    @authenticated
    def post(self, request, format=None):
        """
        Create a new user.

        username -- (REQUIRED) The username for the account
        password -- (REQUIRED) The password for the account
        email -- (REQUIRED) email address
        first_name -- first name
        last_name -- last name
        phone  -- phone number
        mobile_phone  -- mobile phone number
        """
        if settings.CHECK_JWT and settings.CHECK_USER_ADMIN_ROLE and not request.wso2_user_admin:
            return Response(error_dict(msg="Access denied."), status=status.HTTP_401_UNAUTHORIZED)
        serializer = LdapUserSerializer(data=request.DATA)
        # password only required on POST
        if not request.DATA.get("password"):
            serializer.errors['password'] = ["This field is required."]
        if request.DATA.get('username') == "me":
            serializer.errors['username'] = ["me is a reserved and cannot be used for a username."]
        if serializer.is_valid():

            try:
                util.save_ldap_user(serializer=serializer)
            except Error as e:
                return Response(error_dict(msg=e.message), status.HTTP_400_BAD_REQUEST)
            serializer.data.pop("create_time", None)
            serializer.data.pop('password', None)
            create_notification(request.DATA.get('username'), "CREATED", "jstubbs")
            return Response(success_dict(msg="User created successfully.",
                                         result=serializer.data),
                            status=status.HTTP_201_CREATED)
        return Response(error_dict(result=serializer.errors,
                                   msg="Error creating user."), status.HTTP_400_BAD_REQUEST)

class UserDetails(APIView):
    @authenticated
    def get(self, request, username, format=None):
        """
        Retrieve user details
        """
        if request.username and username == "me":
            username = request.username
        LdapUser.base_dn = util.get_base_db(request)
        try:
            user = LdapUser.objects.get(username=username)
        except Exception:
            return Response(error_dict(msg="Error retrieving user details."), status=status.HTTP_404_NOT_FOUND)
        serializer = LdapUserSerializer(user)

        # remove password from data:
        serializer.data.pop('password', None)
        # remove unused uid field as well
        serializer.data.pop('uid', None)
        return Response(success_dict(result=serializer.data, msg="User details retrieved successfully."))

    @authenticated
    def put(self, request, username, format=None):
        """
        Update user details

        email -- (REQUIRED) email address
        password -- The password for the account; should only be passed when updating the password.
        first_name -- first name
        last_name -- last name
        phone  -- phone number
        mobile_phone  -- mobile phone number

        """
        if settings.CHECK_JWT and settings.CHECK_USER_ADMIN_ROLE and not request.wso2_user_admin:
            if not username == request.username:
                create_notification(username, "UPDATED", "jstubbs")
                return Response(error_dict(msg="Access denied."), status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = LdapUser.objects.get(username=username)
        except Exception:
            return Response(error_dict(msg="Error retrieving user details: account not found."),
                            status=status.HTTP_404_NOT_FOUND)

        # we need to add username to the dictionary for serialization, but request.DATA is
        # immutable for PUT requests from some clients (e.g.curl)
        data = request.DATA.copy()
        data['username'] = user.username
        serializer = LdapUserSerializer(user, data=data)
        if serializer.is_valid():
            try:
                util.save_ldap_user(serializer=serializer)
            except Error as e:
                return Response(error_dict(msg=e.message), status.HTTP_400_BAD_REQUEST)
            #remove password from data:
            serializer.data.pop('password', None)
            return Response(success_dict(result=serializer.data,
                                         msg="User updated successfully."),
                            status=status.HTTP_201_CREATED)
        return Response(error_dict(msg="Error updating user.",
                                   result=serializer.errors),
                        status=status.HTTP_400_BAD_REQUEST)

    @authenticated
    def delete(self, request, username, format="json"):
        """
        Delete user
        """
        if settings.CHECK_JWT and settings.CHECK_USER_ADMIN_ROLE and not request.wso2_user_admin:
            if not username == request.username:
                return Response(error_dict(msg="Access denied."), status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = LdapUser.objects.get(username=username)
        except Exception:
            return Response(error_dict(msg="Error deleting user: account not found."),
                            status=status.HTTP_404_NOT_FOUND)
        user.delete()
        create_notification(username, "DELETED", "jstubbs")
        return Response(success_dict(msg="User deleted successfully."))