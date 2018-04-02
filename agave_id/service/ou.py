import logging
from service.models import LdapOU

# Get an instance of a logger
logger = logging.getLogger(__name__)


def create_ou(ou):
    """
    Create an organizational unit in the LDAP db.
    """
    org = LdapOU()
    org.ou = ou
    org.save()

def get_ous():
    logger.debug("top of get_ous")
    try:
        ous = LdapOU.objects.all()
    except Exception as e:
        logger.error("got exception in get_ous. e: {}".format(e))
        return []
    return ous
