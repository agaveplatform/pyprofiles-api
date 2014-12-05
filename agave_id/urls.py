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
    url(r'clients/v2/(?P<client_name>.*[^/])/subscriptions/$', service_views.ClientSubscriptions.as_view(),
        name='client_subscriptions'),
    url(r'clients/v2/(?P<client_name>.*[^/])/subscriptions$', service_views.ClientSubscriptions.as_view()),

    url(r'clients/v2/(?P<client_name>.*[^/])/$', service_views.ClientDetails.as_view()),
    url(r'clients/v2/(?P<client_name>.*[^/])$', service_views.ClientDetails.as_view(), name='client_details'),

    url(r'clients/v2/', service_views.Clients.as_view(), name='clients'),
    url(r'clients/v2', service_views.Clients.as_view()),

    url(r'users/(?P<username>.*[^/])/$', service_views.UserDetails.as_view()),
    url(r'users/(?P<username>.*[^/])$', service_views.UserDetails.as_view()),

    url(r'users/$', service_views.Users.as_view()),
    url(r'users$', service_views.Users.as_view()),

    # admin -- uncomment to activate
    # (r'^admin/', include(admin.site.urls)),
)

urlpatterns = format_suffix_patterns(urlpatterns)