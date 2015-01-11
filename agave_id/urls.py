from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns

from webapp import views as webapp_views
from service import views as service_views

admin.autodiscover()

urlpatterns = patterns('',

    # create an account:
    url(r'^create_account', webapp_views.create_account, name='create_account'),

    # validate an account:
    url(r'^user/validate', webapp_views.user_validate, name='user_validate'),

    # rest API:

    # multi-tenant URLs:
    url(r'(?P<tenant>.*[^/])/users/(?P<username>.*[^/])/$', service_views.UserDetails.as_view()),
    url(r'users/(?P<username>.*[^/])$', service_views.UserDetails.as_view()),

    url(r'(?P<tenant>.*[^/])/users/$', service_views.Users.as_view()),
    url(r'(?P<tenant>.*[^/])/users$', service_views.Users.as_view()),

    url(r'(?P<tenant>.*[^/])/profiles/v2/(?P<username>.*[^/])/$', service_views.UserDetails.as_view()),
    url(r'(?P<tenant>.*[^/])/profiles/v2/(?P<username>.*[^/])$', service_views.UserDetails.as_view()),

    url(r'(?P<tenant>.*[^/])/profiles/v2/$', service_views.Users.as_view()),
    url(r'(?P<tenant>.*[^/])/profiles/v2$', service_views.Users.as_view()),

    # single tenant URLs:
    url(r'users/(?P<username>.*[^/])/$', service_views.UserDetails.as_view()),
    url(r'users/(?P<username>.*[^/])$', service_views.UserDetails.as_view()),

    url(r'users/$', service_views.Users.as_view()),
    url(r'users$', service_views.Users.as_view()),

    url(r'profiles/v2/(?P<username>.*[^/])/$', service_views.UserDetails.as_view()),
    url(r'profiles/v2/(?P<username>.*[^/])$', service_views.UserDetails.as_view()),

    url(r'profiles/v2/$', service_views.Users.as_view()),
    url(r'profiles/v2$', service_views.Users.as_view()),

    url(r'profiles/(?P<username>.*[^/])/$', service_views.UserDetails.as_view()),
    url(r'profiles/(?P<username>.*[^/])$', service_views.UserDetails.as_view()),

    url(r'profiles/$', service_views.Users.as_view()),
    url(r'profiles$', service_views.Users.as_view()),

    url(r'ous/$', service_views.OUs.as_view()),
    url(r'ous$', service_views.OUs.as_view()),
    # admin -- uncomment to activate
    # (r'^admin/', include(admin.site.urls)),
)

urlpatterns = format_suffix_patterns(urlpatterns)