# -*- coding:utf-8 -*-

"""
    some utilities specific to flask
"""

import json, types
from flask import make_response

def json_response(data, status=200, headers={}):
    status = int(status)
    __headers = {'Content-Type': 'application/json'}
    __headers.update(headers)

    if not isinstance(data, types.StringTypes):
        data = json.dumps(dict(data))
    return make_response(data, status, __headers)


def empty_json_response(status=204, headers={}):
    status = int(status)
    __headers = {'Content-Type': 'application/json'}
    __headers.update(headers)
    return make_response('', status, __headers)


class UrlRuleCache(object):
    """
        use this class to cache views for flask (app, blueprint)
        to avoid circular import.

        usage:
            # app/urls/lazy.py
            lazy_urls = UrlRuleCache()

            # app/urls/test_url.py
            from .lazy import lazy_urls

            @lazy_urls.route(r'/index', methods=['GET'])
            def index():
                return 'index'


            # app/app.py
            from flask import Flask
            from .urls.lazy import lazy_urls

            app = Flask(__name__)
            lazy_urls.attach(app)



    """
    def __init__(self, app=None):
        self.app = None
        self.cached_rule = []
        if app:
            self.attach(app)

    def attach(self, app):
        self.app = app
        for rule, endpoint, f, options in self.cached_rule:
            app.add_url_rule(rule, endpoint, f, **options)

    def add_url_rule(self, rule, endpoint, f, **options):
        self.cached_rule.append((rule, endpoint, f, options))

    def route(self, rule, **options):
        def decorator(f):
            endpoint = options.pop('endpoint', None)
            self.add_url_rule(rule, endpoint, f, **options)
            return f
        return decorator


