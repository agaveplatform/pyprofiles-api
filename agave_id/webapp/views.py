__author__ = 'jstubbs'

from django.conf import settings
from django.core.context_processors import csrf
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import render_to_response
from django.views.decorators.http import require_GET, require_http_methods

from agave_id.models import LdapUser
from agave_id.service.util import audit_ldap_user, create_ldap_user, get_email_message, populate_context, save_ldap_user
from common.error import Error
from common.notifications import create_notification
from common.responses import error_response

KEY = '93z3hgk19pwa74m2'

@require_http_methods(["GET", "POST"])
@transaction.commit_manually
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
    user.base_dn = ('ou=tenant' + settings.APP_TENANT_ID + ', '
                        + settings.LDAP_BASE_SEARCH_DN)
    c = populate_context(user, c)
    try:
        audit_ldap_user(user)
    except Error as e:
        c['error'] = e.message
        return render_to_response('create_account.html', c)
    if not request.POST.get("password2") == user.password:
        c['error'] = "Passwords do not match."
        return render_to_response('create_account.html', c)
    try:
        user.password = user.password + KEY + user.nonce
        save_ldap_user(user=user)
    except Error as e:
        c['error'] = e.message
        return render_to_response("create_account.html", c)
    try:
        send_mail(settings.NEW_ACCOUNT_EMAIL_SUBJECT,
                  get_email_message(user),
                  settings.NEW_ACCOUNT_FROM,
                  (user.email, ))
    except Exception as e:
        # delete LdapUser object manually since transaction manager isn't
        # working for ldapdb :-(
        user.delete()
#         transaction.rollback()
        c['error'] = 'Error sending activation email.' + str(e)
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
        create_notification(username, 'CREATED', 'jstubbs')
        return render_to_response('activation.html',{'account_activated':'true'})
    else:
        return render_to_response('activation.html',{'error':'Invalid token'})
