"""Constrain helper function"""


def limit(a, l, u):
    if a > u:
        return u
    elif a < l:
        return l
    else:
        return a


def closure_limit(l, u):
    def limit(a):
        if a > u:
            return u
        elif a < l:
            return l
        else:
            return a

    return limit


def mlimit(a, m):
    if a > m:
        return m
    elif a < -m:
        return -m
    else:
        return a


def closure_mlimit(m):
    def limit(a):
        if a > m:
            return m
        elif a < -m:
            return -m
        else:
            return a

    return limit
