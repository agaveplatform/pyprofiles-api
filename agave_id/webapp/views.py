from __future__ import unicode_literals
__author__ = 'jstubbs'

from django.conf import settings
from django.template.context_processors import csrf
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import render_to_response
from django.views.decorators.http import require_GET, require_http_methods

from service.models import LdapUser
from service.util import audit_ldap_user, create_ldap_user, get_email_message, populate_context, save_ldap_user
from pycommon.error import Error
from pycommon.notifications import create_notification
from pycommon.responses import error_response

KEY = '93z3hgk19pwa74m2'

@require_http_methods(["GET", "POST"])
# @transaction.commit_manually
def create_account(request):
    """
    View to handle account creation in web app.
    """
    c = {}
    c.update(csrf(request))
    c['EMAIL_HOST'] = str(settings.EMAIL_HOST)
    c['EMAIL_PORT'] = str(settings.EMAIL_PORT)
    if request.method == 'GET':
        return render_to_response('create_account.html', c)
    print str(request.POST.get('username'))
    user = create_ldap_user(attrs=request.POST)
    c = populate_context(user, c)
    try:
        audit_ldap_user(user)
    except Error as e:
        c['error'] = e.message
        return render_to_response('create_account.html', c)
    if not request.POST.get("password2") == user.password:
        c['error'] = "Passwords do not match. "
        return render_to_response('create_account.html', c)
    try:
        user.password = user.password + KEY + user.nonce
        save_ldap_user(user=user)
    except Error as e:
        c['error'] = e.message
        return render_to_response("create_account.html", c)

    if settings.CREATE_NOTIFICATIONS:
        create_notification(user.username, 'ACCOUNT_REQUEST', 'guest')

    try:
        send_mail(subject=settings.NEW_ACCOUNT_EMAIL_SUBJECT,
                  message=get_email_message(user),
                  from_email=settings.NEW_ACCOUNT_FROM,
                  recipient_list=(user.email, ),
                  fail_silently=False,
                  auth_user=settings.EMAIL_HOST_USER,
                  auth_password=settings.EMAIL_HOST_PASS)
    except Exception as e:
        # delete LdapUser object manually since transaction manager isn't
        # working for ldapdb :-(
        user.delete()
#         transaction.rollback()
        c['error'] = 'Error sending activation email. ' + str(e)
        return render_to_response("create_account.html", c)
    c['account_created'] = True
    transaction.commit()
    return render_to_response('create_account.html', c)

@require_GET
def user_validate(request):
    """
    Validate an account with the nonce that was sent in the email.
    """
    username = request.GET.get('username')
    nonce = request.GET.get('nonce')
    try:
        u = LdapUser.objects.get(username=username)
    except Exception as e:
        return error_response("Error retrieving username, record not found. "+ str(e))
    if u.nonce == nonce:
        try:
            u.password = u.password[:u.password.find((KEY + u.nonce))]
            u.status= settings.ACTIVE_STATUS
            u.save()
        except Exception as e:
            render_to_response('activation.html',{'error':'Unable to activate account.'})
        if settings.CREATE_NOTIFICATIONS:
            create_notification(username, 'CREATED', username)
        return render_to_response('activation.html',{'account_activated':'true'})
    else:
        return render_to_response('activation.html',{'error':'Invalid token'})
