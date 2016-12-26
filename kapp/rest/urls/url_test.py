# -*- coding:utf-8 -*-

"""
    test url
"""

from flask import request

from kapp.wrapper import json_response, empty_json_response

from .lazy import lazy_app


@lazy_app.route(r'/test', methods=['GET'])
def all_users():
    if request.method == 'GET':
        return json_response({'msg': 'test url handler'})
    else:
        raise Exception, 'not possible'


