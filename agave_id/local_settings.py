"""
These settings are sensitive and/or depend on the deployment so they are kept out of version control. The
local_settings.py.j2 is a jinja2 template that cane be used to generate this file.
"""

import ldap

# -----------------------------------
# API MANAGER INSTANCE CONFIGURATION
# -----------------------------------

# The host name or domain name for the API Manager instance that this instance of the services should
# communicate with.
TENANT_HOST = 'agave-staging.tacc.utexas.edu'
#TENANT_HOST = 'agave-am17-dev.tacc.utexas.edu'

# The ID of the tenant in the LDAP database. This needs to match the userstore configuration in APIM.
APP_TENANT_ID = '1'

# --------------------
# JWT Header settings
# -------------------
# Whether or not to check the JWT; When this is False, certain features will not be available such as the
# "me" lookup feature since these features rely on profile information in the JWT.
CHECK_JWT = True

# Actual header name that will show up in request.META; value depends on APIM configuration, in particular
# the tenant id specified in api-manager.xml
JWT_HEADER = 'HTTP_JWT_ASSERTION'

# Relative location of the public key of the APIM instance; used for verifying the signature of the JWT.
#PUB_KEY = 'usersApp/agave-vdjserver-org_pub.txt'
PUB_KEY = '/home/jstubbs/agave-ldap/src/users/usersApp/agave-vdjserver-org_pub.txt'

# APIM Role required to make updates to the LDAP database
USER_ADMIN_ROLE = 'Internal/user-account-manager'

# Whether or not the USER_ADMIN_ROLE before allowing updates to the LDAP db (/users service)
CHECK_USER_ADMIN_ROLE = True

# These settings are currently only used in the account sign up web application:
# Deprecated - this is only used for manual testing of resolving the tenant id from the JWT.
USE_APP_TENANT_ID = True
# Tenantid key in WSO2 JWT Header:
WSO2_TID_STR = 'enduserTenantId":"'


# -------------------
# LDAP CONFIGURATION
# -------------------
# These settings tell the users service how to bind to the LDAP db and where to store account records

# Use these settings for the LDAP hosted on wso2-elb:
AUTH_LDAP_BIND_DN='uid=admin,ou=system'
AUTH_LDAP_BIND_PASSWORD='secret' # UPDATE FROM STACHE ENTRY
LDAP_BASE_SEARCH_DN='o=agaveapi'

# Use these settings for the LDAP hosted on agaveldap:
# AUTH_LDAP_BIND_DN='cn=Manager, o=agaveapi'
# AUTH_LDAP_BIND_PASSWORD='secret' # UPDATE FROM STACHE ENTRY
# LDAP_BASE_SEARCH_DN='o=agaveapi'

# Status codes for LDAP:
INACTIVE_STATUS = 'Inactive'
ACTIVE_STATUS = 'Active'


# ------------------------------
# GENERAL SERVICE CONFIGURATION
# ------------------------------
# DEBUG = True turns up logging and causes Django to generate excpetion pages with stack traces and
# additional information. Should be False in production.
DEBUG = True

# With this setting activated, Django will not create test databases for any database which has
# the USE_LIVE_FOR_TESTS': True setting.
TEST_RUNNER = 'testrunner.ByPassableDBDjangoTestSuiteRunner'

# ----------------------
# DATABASE CONNECTIVITY
# ----------------------
# The services require two databases to operate:
#   i. A MySQL db for the client data (this should be shared by the APIM instance)
#   ii. An LDAP db for the user profile data.

DATABASES = {
    # The 'default' db is the MySQL database.
    # Use this setting to connect to the APIM db (almost always what you want to do)
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'apimgtdb',
        'USER': 'superadmin',
        'PASSWORD': 'password', # UPDATE FROM STACHE ENTRY
        'HOST': TENANT_HOST,
        'PORT': '3306',
        # When running the test suite, when this setting is True, the test runner will not create a
        # test database. This is required for the clients service tests, since that service relies on
        # interactions with the APIM instance itself. If the clients service is writing data to a
        # test db then APIM will not see those data and the tests will fail.
        'USE_LIVE_FOR_TESTS': True,
    },

    # It is possible to run the users service, with limited functionality, using a sqlite3 db; use this
    # setting to do that. Note that the clients service will not be functional in this mode.
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': 'userAppDB',
    # },

    # The 'ldap' entry is for the LDAP db.
    # Use this setting to connect to the LDAP hosted on wso2-elb:
    'ldap': {
        'ENGINE': 'ldapdb.backends.ldap',
        'NAME': 'ldap://129.114.60.212:10389',
        'USER': AUTH_LDAP_BIND_DN,
        'PASSWORD': AUTH_LDAP_BIND_PASSWORD,
        'TLS': False,
        'CONNECTION_OPTIONS': {
            ldap.OPT_X_TLS_DEMAND: False,
        }
     }

    # Use this setting to connect to the LDAP hosted on agaveldap:
    # 'ldap': {
    #     'ENGINE': 'ldapdb.backends.ldap',
    #     'NAME': 'ldaps://agaveldap.tacc.utexas.edu:636'',
    #     'USER': AUTH_LDAP_BIND_DN,
    #     'PASSWORD': AUTH_LDAP_BIND_PASSWORD,
    #     'TLS': False,
    #     'CONNECTION_OPTIONS': {
    #         ldap.OPT_X_TLS_DEMAND: False,
    #     }
    #  }


}

# ------------------
# BEANSTALK INSTANCE
# ------------------
BEANSTALK_SERVER = "iplant-qa.tacc.utexas.edu"
BEANSTALK_PORT = 11300
# BEANSTALK_TUBE = 'default'
BEANSTALK_TUBE = 'test.jfs'
BEANSTALK_SRV_CODE = '0001-001'
TENANT_UUID = '0001411570898814'

# ----------------------
# WEB APP CONFIGURATION
# ----------------------
# These settings are only used when deploying the account sign up web application:
APP_BASE = 'http://localhost:8000'
NEW_ACCOUNT_EMAIL_SUBJECT='New Agave Account Requested'
NEW_ACCOUNT_FROM = 'do-not-reply@agaveapi.io'
STATIC_ROOT = '/home/apim/agave-ldap/src/users/static'

# SMTP - used for the email loop account verification:
# Run the python smtp server with
# python -m smtpd -n -c DebuggingServer localhost:1025
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_BASE_URL = 'http://agave-staging.tacc.utexas.edu'