# -*- coding:utf-8 -*-


def is_subdict(con, sub):
    """
        usage:
            is_subdict({'a':1, 'b':2}, {'a':1}) # True
            is_subdict({'a':1, 'b':2}, {'a':1, 'c':3}) # False
    """
    for key, value in sub.iteritems():
        if not con.has_key(key):
            return False
        if con[key] != value:
            return False

    return True

def merge_dicts(*dicts):
    """
        usage:
            new_d = merge_dicts({'a':1, 'b':2}, {'a':11, 'c':3})
            print new_d # {'a': 11, 'b': 2, 'c': 3}
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result

def dict_has_keys(d, keys):
    """
        usage:
            dict_has_keys({'a':1, 'b':2, 'c': 3}, ['a', 'b']) # True
            dict_has_keys({'a':1, 'b':2, 'c': 3}, ['a', 'e']) # False
    """
    if not isinstance(keys, (list, tuple)):
        keys = [keys]
    # return all (key in d for key in keys)
    for key in keys:
        if not d.has_key(key):
            return False
    return True

def sub_dict(d, *keys):
    """
        usage:
            sd = sub_dict({'a': 1, 'b':2 , 'c':3}, ['a', 'e'])
            print sd    # {'a': 1}
    """
    return dict((key, d[key]) for key in keys if key in d)
