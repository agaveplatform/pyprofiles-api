# Run this script to diff two or more ldap servers.

SERVERS = ['ldaps://agaveldap01.tacc.utexas.edu:636',
           'ldaps://agaveldap02.tacc.utexas.edu:636',
           'ldaps://agaveldap03.tacc.utexas.edu:636',
]

import timeit

import ldap



def get_user_from_server(user, s):
    """look up a single ldap record `user` from server `s`. """

    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    l = ldap.initialize(uri=s)
    # first entry is the dn:
    try:
        u = l.search_s(base=user[0], scope=ldap.SCOPE_BASE)
    except Exception:
        return 0
    if len(u) < 1:
        return 0
    if len(u) > 1:
        return 2
    return u[0]

def compare_attrs(u1, u2, diffs, problems):
    """Compare attrs on two ldap tuples."""
    for k,v in u1[1].items():
        if k not in u2[1].items():
            diffs += 1
            print("Attr {} missing - R1: {}, R2: {}".format(k, u1, u2))
        elif not u1[1][k] == u2[1][k]:
            diffs += 1
            print("Attr {} different - R1: {}, R2: {}".format(k, u1, u2))


def compare(u1, u2, diffs, problems):
    """compare two ldap tuples"""
    if not u1[0] == u2[0]:
        # dn's are different, should never happen:
        print("Problem, tried to compare two records with different DNs. R1: {}, R2: {}".format(u1[0],u2[0]))
        problems += 1
        return
    # compare_attrs(u1, u2, diffs, problems)
    # compare_attrs(u2, u1, diffs, problems)


def main():
    start = timeit.default_timer()
    users = []
    diffs = 0
    problems = 0
    records = 0
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    for idx, server in enumerate(SERVERS):
        # if records > 1:
        #     break
        l = ldap.initialize(uri=server)
        users = l.search_s(base='o=agaveapi', scope=ldap.SCOPE_SUBTREE)
        for user in users:
            records += 1
            # if records > 2:
            #     break
            for jdx, s2 in enumerate(SERVERS):
                if jdx == idx:
                    continue
                result = get_user_from_server(user, s2)
                if result == 0:
                    diffs += 1
                    print("Record {} was in server {} but not in server {}".format(str(user[0]), server, s2))
                elif result == 2:
                    diffs += 1
                    print("Problem -- multiple records found")
                else:
                    compare(user, result, diffs, problems)
    stop = timeit.default_timer()
    tot = stop - start
    print 'RESULTS:'
    print('Time: {}'.format(tot))
    print('Records: {}'.format(records))
    print('Diffs: {}'.format(diffs))
    print('Problems: {}'.format(problems))


if __name__ == '__main__':
    main()