__author__ = 'jstubbs'


# Django settings for Agave identity provider project
import os
# from django_auth_ldap.config import LDAPSearch

# sensitive settings: first look for 'deployment_settings', then 'local_settings',
# finally 'local_settings_example' which should always be there
try:
    from deployment_settings import *
except:
    try:
        from local_settings import *
    except:
        from local_settings_example import *

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DEBUG = DEBUG
APPEND_SLASH = False


ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# This setting is required to direct ORM appropriately when running multiple DBs.
# Note: It only handles one LDAP DB; if multiple LDAPs are needed, you will
# have to update this router.
DATABASE_ROUTERS = ['ldapdb.router.Router']

# Order matters here - first authentication 'success' sticks.
AUTHENTICATION_BACKENDS = (
    # 'django_auth_ldap.backend.LDAPBackend',
    # 'django.contrib.auth.backends.ModelBackend',
)



# ---------------------------
# EMAIL server configuration
# ---------------------------
# Find these settings in the dev and deployment settings.

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['*']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
# STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'f051g-_7@!1l*hg#ilfa@op+z3+6ydlgb0%p(k-nb7ci7l!fb)'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
     'django.contrib.messages.context_processors.messages',
     'django.contrib.auth.context_processors.auth',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'agave_id.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'agave_id.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(CURRENT_DIR, 'templates'),
    os.path.join(CURRENT_DIR, 'webapp', 'templates'),
)

LOGIN_URL = 'login'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'agave_id.service',
    'agave_id.webapp',
    'django.contrib.admin',
    'rest_framework',
    'corsheaders',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console':{
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'agave_id': {
            'handlers': ['console', 'null'],
            'propagate': True,
            'level': 'DEBUG',
        },
    }
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
}

CORS_ORIGIN_ALLOW_ALL = True


# Import the sensitive settings again because the settings.py file may have overwritten some.
try:
    from deployment_settings import *
except:
    try:
        from local_settings import *
    except:
        from local_settings_example import *
