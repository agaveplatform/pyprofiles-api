"""
This is an example of the local_settings.py file and provides a minimal configuration to run the
service locally. Rename as local_settings.py and update as necessary for a production deployment.
"""

import ldap
import os

# --------
# TENANCY
# --------
# Whether or not to run in MULTI-TENANT mode. If True, the service will require a tenant id in the
# URL. If False, the service will use the APP_TENANT_ID setting below.
MULTI_TENANT = False

# The ID of the tenant in the LDAP database. This needs to match the userstore configuration in APIM.
# This setting is only used when the MULTI_TENANT setting is False.
APP_TENANT_ID = os.environ.get('ldap_tenant_id', '1')

# Whne true, the services will not make any updates.
READ_ONLY = os.environ.get('agave_id_read_only', False)

# --------------------
# JWT Header settings
# -------------------
# Whether or not to check the JWT; When this is False, certain features will not be available such as the
# "me" lookup feature since these features rely on profile information in the JWT.
CHECK_JWT = os.environ.get('check_jwt', False)

# Actual header name that will show up in request.META; value depends on APIM configuration, in particular
# the tenant id specified in api-manager.xml
JWT_HEADER = os.environ.get('jwt_header', 'HTTP_JWT_ASSERTION')

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
AUTH_LDAP_BIND_DN = u'cn=admin,dc=agaveapi'
AUTH_LDAP_BIND_PASSWORD = u'p@ssword'
LDAP_BASE_SEARCH_DN = u'dc=agaveapi'

# Set USE_CUSTOM_LDAP = True to use a database with a different schema than the traditional Agave ldap. Some
# fields are still required, for example the uid field as the primary key.
USE_CUSTOM_LDAP = os.environ.get('use_custom_ldap', False)

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
# TEST_RUNNER = 'agave_id.testrunner.ByPassableDBDjangoTestSuiteRunner'


# ------------------
# BEANSTALK INSTANCE
# ------------------
CREATE_NOTIFICATIONS = True
BEANSTALK_SERVER = "iplant-qa.tacc.utexas.edu"
BEANSTALK_PORT = 11300
BEANSTALK_TUBE = 'test.jfs'
BEANSTALK_SRV_CODE = '0001-001'
TENANT_UUID = os.environ.get('tenant_uuid', '0001411570898814')


# ----------------------
# DATABASE CONNECTIVITY
# ----------------------

# for running in docker, need to get the ldap db connectivity data from the environment:
HERE = os.path.dirname(os.path.realpath(__file__))

AUTH_LDAP_BIND_DN = os.environ.get('auth_ldap_bind_dn', AUTH_LDAP_BIND_DN)
AUTH_LDAP_BIND_PASSWORD = os.environ.get('auth_ldap_bind_password', AUTH_LDAP_BIND_PASSWORD)
LDAP_BASE_SEARCH_DN = os.environ.get('ldap_base_search_dn', LDAP_BASE_SEARCH_DN)

# unless the USE_ALTERNATE_LDAP setting is made, update the search dn for the standard Agave ldap structure:
print "use_custom_ldap:", str(USE_CUSTOM_LDAP)
if not USE_CUSTOM_LDAP:
    LDAP_BASE_SEARCH_DN = 'ou=tenant' + APP_TENANT_ID + ',' + LDAP_BASE_SEARCH_DN

print "using LDAP_BASE_SEARCH_DN:", LDAP_BASE_SEARCH_DN

# if tenant_id has been defined in the environment used that, otherwise, default to 'dev':
TENANT_ID = os.environ.get('tenant_id', 'dev')


if os.path.exists(os.path.join(HERE, 'running_in_docker')):
# first, check to see if links are available (either from fig or directly from docker):
    if os.environ.get('LDAP_PORT'):
        db_name = os.environ['LDAP_PORT']
        if db_name.startswith('tcp://'):
            db_name = 'ldap://' + db_name[6:]
    # otherwise, use service discovery:
    else:
        db_name = 'ldap.apim.' + TENANT_ID + '.agave.tacc.utexas.edu:'
        if os.environ.get('use_ldaps'):
            db_name = 'ldaps://' + db_name + '636'
        else:
            db_name = 'ldap://' + db_name + '389'
        # alo use service discovery for beastalk:
        BEANSTALK_SERVER = 'beanstalk.' + TENANT_ID + '.agave.tacc.utexas.edu'
else:
    db_name = 'ldap://localhost:10389'

db_name = unicode(db_name)
LDAP_BASE_SEARCH_DN = unicode(LDAP_BASE_SEARCH_DN)
AUTH_LDAP_BIND_DN = unicode(AUTH_LDAP_BIND_DN)
AUTH_LDAP_BIND_PASSWORD = unicode(AUTH_LDAP_BIND_PASSWORD)

print("Using db_name: {}".format(db_name))


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
