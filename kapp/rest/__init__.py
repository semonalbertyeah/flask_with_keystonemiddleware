# -*- coding:utf-8 -*-

"""
    a sub-app template.
"""

import os
import json
from flask import Blueprint

from . import urls

mod = Blueprint('rest', __name__)
urls.attach_url(mod)

CUR_DIR = os.path.dirname(os.path.abspath(__file__))


__all__ = [
    'mod'
]
