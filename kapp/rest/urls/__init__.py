# -*- coding:utf-8 -*-

"""
    this package contain all url rules' definition.
"""

import os, importlib
from .lazy import lazy_app



CUR_DIR = os.path.dirname(os.path.abspath(__file__))


# import all submodules whose name starts with "url_"
# these modules contain registered url rules.
url_mod_names = [".%s" % mn[:-3]
                 for mn in os.listdir(CUR_DIR) \
                 if mn.startswith('url_') and mn.endswith('.py')]
for mn in url_mod_names:
    importlib.import_module(mn, __package__)


def attach_url(app):
    lazy_app.attach(app)
