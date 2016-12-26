# -*- coding:utf-8 -*-

"""
    vmd user rest api
"""

from flask import request

from vmd_rest.wrapper import json_response, empty_json_response

from .. import vmd_db as db
from ..vmd_db import VMDDBError
from ..mission import Mission, execute_mission
from .lazy import lazy_app


@lazy_app.route(r'/test', methods=['GET'])
def all_users():
    if request.method == 'GET':
        return json_response({'msg': 'test url handler'})
    else:
        raise Exception, 'not possible'


