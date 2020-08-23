"""
This is an example of the local_settings.py file and provides a minimal configuration to run the
service locally. Rename as local_settings.py and update as necessary for a production deployment.
"""
import ldap
import os
import requests
# --------
# TENANCY
# --------
# Whether or not to run in MULTI-TENANT mode. If True, the service will require a tenant id in the
# URL. If False, the service will use the APP_TENANT_ID setting below.
MULTI_TENANT = False

# The ID of the tenant in the LDAP database. This needs to match the userstore configuration in APIM.
# This setting is only used when the MULTI_TENANT setting is False.
APP_TENANT_ID = os.environ.get('ldap_tenant_id', '1')

# When true, the services will not make any updates.
READ_ONLY = os.environ.get('agave_id_read_only', False)

# --------------------
# JWT Header settings
# -------------------
AUTH_FUNC = os.environ.get('AGAVE_AUTH_TYPE', None)
if not AUTH_FUNC:
    AUTH_FUNC = os.environ.get('auth_function', None)

print "auth_function:", str(AUTH_FUNC)

# --------------------
# JWT Header settings
# -------------------
# Whether or not to check the JWT; When this is False, certain features will not be available such as the
# "me" lookup feature since these features rely on profile information in the JWT.
CHECK_JWT = os.environ.get('check_jwt', False)

# Actual header name that will show up in request.META; value depends on APIM configuration, in particular
# the tenant id specified in api-manager.xml
JWT_HEADER = os.environ.get('jwt_header', u'HTTP_JWT_ASSERTION')

# Relative location of the public key of the APIM instance; used for verifying the signature of the JWT.
#PUB_KEY = 'usersApp/agave-vdjserver-org_pub.txt'
PUB_KEY = u'/home/apim/public_keys/apim_default.pub'
if os.environ.get('PUB_KEY_PATH'):
    PUB_KEY = unicode(os.environ.get('PUB_KEY_PATH'))
elif os.environ.get('PUB_KEY_URL'):
    try:
        pk_resp = requests.get(str(os.environ.get('PUB_KEY_URL')))
        if pk_resp.status_code == 200:
            pub_key_value = pk_resp.text
            os.makedirs(u'/home/apim/public_keys')
            PUB_KEY = '/home/apim/public_keys/' + APP_TENANT_ID + '.pub'
            with os.open(PUB_KEY) as f:
                os.write(f, pk_resp.text)
                os.close(f)
                print ("Successfully fetched public key from {}. Cached to disk at: {}".format(os.environ.get('PUB_KEY_URL'), PUB_KEY))
        else:
            msg = "{}: {}".format(pk_resp.status_code, pk_resp.text)
            raise Exception(msg)
    except Exception as e:
        print ("Failed to fetch public key from {}, JWT validation will fail.".format(os.environ.get('PUB_KEY_URL')))
        print (str(e.message))

# APIM Role required to make updates to the LDAP database
USER_ADMIN_ROLE = unicode(os.environ.get('USER_ADMIN_ROLE', u'Internal/user-account-manager'))

# Whether or not to check for the USER_ADMIN_ROLE before allowing updates to the LDAP db (/users service)
CHECK_USER_ADMIN_ROLE = False


# ------------------------------
# GENERAL SERVICE CONFIGURATION
# ------------------------------
# Base URL of this instance of the service. Used to populate the hyperlinks in the responses.
# TODO: this should be pulled from the tenant table in the agave core service db and cross-referenced
# with the X

APP_BASE = os.environ.get('APP_BASE', u'http://localhost:8000')

# Enable using forwarding headers when running behind proxy
#USE_X_FORWARDED_HOST = False
#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', u'https')

# DEBUG = True turns up logging and causes Django to generate exception pages with stack traces and
# additional information. Should be False in production.
DEBUG = True

# With this setting activated, Django will not create test databases for any database which has
# the USE_LIVE_FOR_TESTS': True setting.
TEST_RUNNER = 'testrunner.ByPassableDBDjangoTestSuiteRunner'


# ------------------
# BEANSTALK INSTANCE
# ------------------
CREATE_NOTIFICATIONS = True
BEANSTALK_SERVER = os.environ.get('IPLANT_MESSAGING_HOST', "beanstalkd")
BEANSTALK_PORT = int(os.environ.get('IPLANT_MESSAGING_PORT','11300'))
BEANSTALK_TUBE = os.environ.get('IPLANT_NOTIFICATION_SERVICE_QUEUE', 'dev.notifications.queue')
BEANSTALK_SRV_CODE = '0001-001'
TENANT_UUID = os.environ.get('tenant_uuid', '0001411570898814')


# -------------------
# LDAP CONFIGURATION
# -------------------
# These settings tell the users service how to bind to the LDAP db and where to store account records

# Set USE_CUSTOM_LDAP = True to use a database with a different schema than the traditional Agave ldap. Some
# fields are still required, for example the uid field as the primary key.
USE_CUSTOM_LDAP = os.environ.get('use_custom_ldap', False)

# Status codes for LDAP:
INACTIVE_STATUS = u'Inactive'
ACTIVE_STATUS = u'Active'

# for running in docker, need to get the ldap db connectivity data from the environment:
HERE = os.path.dirname(os.path.realpath(__file__))

AUTH_LDAP_BIND_DN = os.environ.get('auth_ldap_bind_dn', u'cn=admin,dc=agaveapi')
AUTH_LDAP_BIND_PASSWORD = os.environ.get('auth_ldap_bind_password', u'p@ssword')
LDAP_BASE_SEARCH_DN = os.environ.get('ldap_base_search_dn', u'dc=agaveapi')

# unless the USE_ALTERNATE_LDAP setting is made, update the search dn for the standard Agave ldap structure:
print "use_custom_ldap:", str(USE_CUSTOM_LDAP)
if not USE_CUSTOM_LDAP:
    LDAP_BASE_SEARCH_DN = 'ou=tenant' + APP_TENANT_ID + ',' + LDAP_BASE_SEARCH_DN

print "using LDAP_BASE_SEARCH_DN:", LDAP_BASE_SEARCH_DN

# if tenant_id has been defined in the environment used that, otherwise, default to 'dev':
TENANT_ID = os.environ.get('AGAVE_DEDICATED_TENANT_ID')
if not TENANT_ID:
    TENANT_ID = os.environ.get('tenant_id', 'agave.dev')

API_VERSION = os.environ.get('AGAVE_API_VERSION', os.environ.get('AGAVE_VERSION'))
if not API_VERSION:
    API_VERSION = os.environ.get('api_version', '2.2.27-develop')


if os.path.exists(os.path.join(HERE, 'running_in_docker')):
# first, check to see if links are available (either from docker compose or directly from docker):
    if os.environ.get('LDAP_PORT'):
        db_name = os.environ['LDAP_PORT']
        if db_name.startswith('tcp://'):
            db_name = 'ldap://' + db_name[6:]
    # otherwise, use service discovery:
    else:
        db_name = 'ldap'
        if os.environ.get('use_ldaps'):
            db_name = 'ldaps://' + db_name + '636'
        else:
            db_name = 'ldap://' + db_name + '389'
else:
    if os.environ.get('LDAP_PORT'):
        db_name = os.environ['LDAP_PORT']
        if db_name.startswith('tcp://'):
            db_name = 'ldap://' + db_name[6:]
    else:
        db_name = 'ldap://localhost:10389'

print "Using db_name: ", db_name

MAX_PAGE_SIZE = int(os.environ.get('IPLANT_MAX_PAGE_SIZE', '250'))
DEFAULT_PAGE_SIZE = int(os.environ.get('IPLANT_DEFAULT_PAGE_SIZE', '100'))

DATABASES = {
    # Django requires a default db which we leave as the sql-lite default.
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(HERE, 'agave_id_sql'),
    },

    # Use this setting to connect to an LDAP running in a docker container:
    'ldap': {
        'ENGINE': 'ldapdb.backends.ldap',
        'NAME': unicode(db_name),
        'USER': unicode(AUTH_LDAP_BIND_DN),
        'PASSWORD': unicode(AUTH_LDAP_BIND_PASSWORD),
        'TLS': False,
        'CONNECTION_OPTIONS': {
            ldap.OPT_X_TLS_DEMAND: False,
            'page_size': DEFAULT_PAGE_SIZE
        }
    },
}

# ----------------------
# WEB APP CONFIGURATION
# ----------------------
# These settings are only used when deploying the account sign up web application:
NEW_ACCOUNT_EMAIL_SUBJECT=os.environ.get('New Agave Account Requested')
NEW_ACCOUNT_FROM = os.environ.get('MAIL_SMTPS_FROM_ADDRESS', 'no-reply@agaveplatform.org')
# NEW_ACCOUNT_FROM_NAME = os.environ.get('MAIL_SMTPS_FROM_NAME','Agave Platform')
# if NEW_ACCOUNT_FROM_NAME:
#     NEW_ACCOUNT_FROM = "%s <%s>".format(NEW_ACCOUNT_FROM_NAME, NEW_ACCOUNT_FROM)

EMAIL_BASE_URL = APP_BASE
EMAIL_HOST_USER = os.environ.get('MAIL_SMTPS_USER', u'agavedev')
EMAIL_HOST_PASS = os.environ.get('MAIL_SMTPS_PASSWD', u'password')

STATIC_ROOT = os.path.join(HERE,'static')

# SMTP - used for the email loop account verification:
# Points to the maildev container in the compose file by default.
# Non SSL port 10025 locally, 25 remote
if os.path.exists(os.path.join(HERE, 'running_in_docker')):
    mail_server = os.environ.get('MAIL_SMTPS_HOST', u'maildev')
    mail_server_port = os.environ.get('MAIL_SMTPS_PORT', 25)
else:
    mail_server = os.environ.get('MAIL_SMTPS_HOST', u'localhost')
    mail_server_port = os.environ.get('MAIL_SMTPS_PORT', 10025)

# print "Using:", mail_server, "on port:", str(mail_server_port)
EMAIL_HOST = mail_server
EMAIL_PORT = mail_server_port
