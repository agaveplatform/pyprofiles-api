
from agave_id.models import LdapOU

def create_ou(ou):
    """
    Create an organizational unit in the LDAP db.
    """
    org = LdapOU()
    org.ou = ou
    org.save()

def get_ous():
    ous = LdapOU.objects.all()
    return ous
