"""
This is an example of the local_settings.py file and provides a minimal configuration to run the
service locally. Rename as local_settings.py and update as necessary for a production deployment.
"""

import ldap

# --------
# TENANCY
# --------
# Whether or not to run in MULTI-TENANT mode. If True, the service will require a tenant id in the
# URL. If False, the service will use the APP_TENANT_ID setting below.
MULTI_TENANT = False

# The ID of the tenant in the LDAP database. This needs to match the userstore configuration in APIM.
# This setting is only used when the MULTI_TENANT setting is False.
APP_TENANT_ID = '1'

# --------------------
# JWT Header settings
# -------------------
# Whether or not to check the JWT; When this is False, certain features will not be available such as the
# "me" lookup feature since these features rely on profile information in the JWT.
CHECK_JWT = False

# Actual header name that will show up in request.META; value depends on APIM configuration, in particular
# the tenant id specified in api-manager.xml
JWT_HEADER = 'HTTP_JWT_ASSERTION'

# Relative location of the public key of the APIM instance; used for verifying the signature of the JWT.
#PUB_KEY = 'usersApp/agave-vdjserver-org_pub.txt'
PUB_KEY = '/home/apim/public_keys/apim_default.pub'

# APIM Role required to make updates to the LDAP database
USER_ADMIN_ROLE = 'Internal/user-account-manager'

# Whether or not the USER_ADMIN_ROLE before allowing updates to the LDAP db (/users service)
CHECK_USER_ADMIN_ROLE = True


# -------------------
# LDAP CONFIGURATION
# -------------------
# These settings tell the users service how to bind to the LDAP db and where to store account records

# Use these settings for the LDAP on localhost running out of docker:
AUTH_LDAP_BIND_DN='cn=admin,dc=agaveapi'
AUTH_LDAP_BIND_PASSWORD='p@ssword'
LDAP_BASE_SEARCH_DN='dc=agaveapi'

# Status codes for LDAP:
INACTIVE_STATUS = 'Inactive'
ACTIVE_STATUS = 'Active'

# ------------------------------
# GENERAL SERVICE CONFIGURATION
# ------------------------------
# Base URL of this instance of the service. Used to populate the hyperlinks in the responses.
APP_BASE = 'http://localhost:8000'

# DEBUG = True turns up logging and causes Django to generate excpetion pages with stack traces and
# additional information. Should be False in production.
DEBUG = True

# With this setting activated, Django will not create test databases for any database which has
# the USE_LIVE_FOR_TESTS': True setting.
TEST_RUNNER = 'agave_id.testrunner.ByPassableDBDjangoTestSuiteRunner'


# ----------------------
# DATABASE CONNECTIVITY
# ----------------------

# get the port of the ldap db from the environment:
import os
HERE = os.path.dirname(os.path.realpath(__file__))

if os.path.exists(os.path.join(HERE, 'running_in_docker')):
# first, check to see if links are available (either from fig or directly from docker):
    if os.environ.get('LDAP_PORT'):
        db_name = os.environ['LDAP_PORT']
        if db_name.startswith('tcp://'):
            db_name = 'ldap://' + db_name[6:]
    # otherwise, use service discovery:
    else:
        # if tenant_id has been defined in the environment used that, otherwise, default to 'dev':
        tenant_id = os.environ.get('tenant_id', 'dev')
        db_name = 'ldap.apim.' + tenant_id + '.agave.tacc.utexas.edu:389'
else:
    db_name = 'ldap://localhost:10389'

print "Using db_name: ", db_name

DATABASES = {
    # Django requires a default db which we leave as the sql-lite default.
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(HERE, 'agave_id_sql'),
    },

    # Use this setting to connect to an LDAP running in a docker container:
    'ldap': {
        'ENGINE': 'ldapdb.backends.ldap',
        'NAME': db_name,
        'USER': AUTH_LDAP_BIND_DN,
        'PASSWORD': AUTH_LDAP_BIND_PASSWORD,
        'TLS': False,
        'CONNECTION_OPTIONS': {
            ldap.OPT_X_TLS_DEMAND: False,
        }
    },
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
NEW_ACCOUNT_EMAIL_SUBJECT='New Agave Account Requested'
NEW_ACCOUNT_FROM = 'do-not-reply@agaveapi.io'
STATIC_ROOT = os.path.join(HERE,'static')

# SMTP - used for the email loop account verification:
# Run the python smtp server with
# python -m smtpd -n -c DebuggingServer localhost:1025
# run an smtp server reachable by a docker container:
# python -m smtpd -n -c DebuggingServer 172.17.42.1:1025

if os.path.exists(os.path.join(HERE, 'running_in_docker')):
    # mail_server = os.environ.get('HOST_IP')
    mail_server = os.environ.get('HOST_IP') or '172.17.42.1'
else:
    mail_server = 'localhost'
# mail_server = 'localhost'
mail_server_port = 1025

# print "Using:", mail_server, "on port:", str(mail_server_port)
EMAIL_HOST = mail_server
EMAIL_PORT = mail_server_port
EMAIL_BASE_URL = 'http://localhost:8000'
