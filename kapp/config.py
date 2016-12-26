# -*- coding:utf-8 -*-

from oslo_config import cfg

"""
    openstack components typically use oslo_config.cfg.CONF as global config object.
"""

# better make it read-only
CONF = cfg.CONF
