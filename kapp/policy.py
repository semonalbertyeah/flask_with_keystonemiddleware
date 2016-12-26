# -*- coding:utf-8 -*-

"""
    apply oslo.policy to flask app
"""

import json
from werkzeug.local import LocalProxy
from paste.deploy.converters import asbool
from flask import current_app, request, _request_ctx_stack, abort
from oslo_policy import policy
from oslo_config import cfg

from .wrapper import json_response

from .config import CONF


def get_creds_from_request(req):
    """
        get credential info from http request headers -> (generated from keystonemiddleware)
        compatible with v2,v3
        input:
            req -> flask.request
    """
    headers = req.headers
    identity_status = headers.get('x-identity-status', None) or \
                        headers['x-service-identity-status']
    if identity_status.lower() != 'confirmed':
        return {
            'identity_status': identity_status
        }

    token = headers.get('x-auth-token', None) or \
                        headers.get('x-service-token', None)
    domain_id = headers.get('x-domain-id', None) or \
                        headers.get('x-service-domain-id', None)
    domain_name = headers.get('x-domain-name', None) or \
                        headers.get('x-service-domain-name', None)

    project_id = headers.get('x-project-id', None) or \
                        headers.get('x-service-project-id', None)
    project_name = headers.get('x-project-name', None) or \
                        headers.get('x-service-project-name', None)
    project_domain_id = headers.get('x-project-domain-id', None) or \
                        headers.get('x-service-project-domain-id', None)
    project_domain_name = headers.get('x-project-domain-name', None) or \
                        headers.get('x-service-project-domain-name', None)

    user_id = headers.get('x-user-id', None) or \
                        headers.get('x-serice-user-id', None)
    user_name = headers.get('x-user-name', None) or \
                        headers.get('x-service-user-name') or \
                        headers.get('x-user')
    user_domain_id = headers.get('x-user-domain-id', None) or \
                        headers.get('x-service-user-domain-id', None)
    user_domain_name = headers.get('x-user-domain-name', None) or \
                        headers.get('x-service-user-domain-name', None)

    tenant_id = headers.get('x-tenant-id', None) or \
                        headers.get('x-tenant')
    tenant_name = headers.get('x-tenant-name', None)

    roles = headers.get('x-roles', None) or \
                        headers.get('x-service-roles', None)
    is_admin = headers.get('x-is-admin-project', None)
    service_catalog = headers.get('x-service-catalog', None)

    assert token
    creds = {
        'token': {
            'id': token
        }
    }

    if domain_id is not None:
        creds.setdefault('domain', {})['id'] = domain_id
    if domain_name is not None:
        creds.setdefault('domain', {})['name'] = domain_name

    if project_id is not None:
        creds.setdefault('project', {})['id'] = project_id
    if project_name:
        creds.setdefault('project', {})['name'] = project_name
    if project_domain_id is not None:
        creds.setdefault('project', {}).setdefault('domain', {})['id'] = project_domain_id
    if project_domain_name is not None:
        creds.setdefault('project', {}).setdefault('domain', {})['name'] = project_domain_name

    if user_id is not None:
        creds.setdefault('user', {})['id'] = user_id
    if user_name is not None:
        creds.setdefault('user', {})['name'] = user_name
    if user_domain_id is not None:
        creds.setdefault('user', {}).setdefault('domain', {})['id'] = user_domain_id
    if user_domain_name is not None:
        creds.setdefault('user', {}).setdefault('domain', {})['name'] = user_domain_name

    if tenant_id is not None:
        creds.setdefault('tenant', {})['id'] = tenant_id
    if tenant_name is not None:
        creds.setdefault('tenant', {})['name'] = tenant_name

    if roles is not None:
        creds['roles'] = roles.split(',')
    if is_admin is not None:
        creds['is_admin'] = asbool(is_admin)
    if service_catalog is not None:
        creds['service_catalog'] = json.loads(service_catalog)

    creds['identity_status'] = identity_status

    return creds


def init_target_conf():
    global CONF
    if 'policy_target' in CONF:
        return

    # register oslo config sections -> policy_target, for target info
    policy_target_group = cfg.OptGroup(name='policy_target')
    CONF.register_group(policy_target_group)
    CONF.register_opts([
        cfg.StrOpt('target_role', default=None),
        cfg.StrOpt('target_project_name', default=None),
        cfg.StrOpt('target_project_id', default=None),
        cfg.StrOpt('target_project_domain_name', default=None),
        cfg.StrOpt('target_project_domain_id', default=None),
        cfg.StrOpt('target_tenant_id', default=None),
        cfg.StrOpt('target_tenant_name', default=None),
        cfg.BoolOpt('enabled', default=True)
    ], policy_target_group)


def get_target_info():
    global CONF
    init_target_conf()

    target = {}
    if CONF.policy_target.target_role is not None:
        target['target_role'] = CONF.policy_target.target_role

    if CONF.policy_target.target_project_name is not None:
        target['target_project_name'] = CONF.policy_target.target_project_name

    if CONF.policy_target.target_project_id is not None:
        target['target_project_id'] = CONF.policy_target.target_project_id

    if CONF.policy_target.target_project_domain_name is not None:
        target['target_project_domain_name'] = CONF.policy_target.target_project_domain_name

    if CONF.policy_target.target_project_domain_id is not None:
        target['target_project_domain_id'] = CONF.policy_target.target_project_domain_id

    if CONF.policy_target.target_tenant_name is not None:
        target['target_tenant_name'] = CONF.policy_target.target_tenant_name

    if CONF.policy_target.target_tenant_id is not None:
        target['target_tenant_id'] = CONF.policy_target.target_tenant_id


    return target

service_target_info = LocalProxy(get_target_info)



def init_policy(app):
    """
        input:
            app -> flask app

        output:
            app.policy_enforcer
    """
    init_target_conf()
    if not CONF.policy_target.enabled:
        return

    enforcer = policy.Enforcer(CONF)
    enforcer.load_rules()
    app.policy_enforcer = enforcer


    @app.before_request
    def check_policy():
        serv_name = 'kapp'
        overall_op = 'all'
        overall_rule = '%s:%s' % (serv_name, overall_op)

        # get credential from headers
        creds = get_creds_from_request(request)

        # store creds in request context, for other usage
        _request_ctx_stack.top.creds = creds    

        if not enforcer.enforce(overall_rule, service_target_info, creds):
            # abort(403, 'policy checking failed.')
            return json_response({
                "error": {
                    "message": "policy checking failed",
                    "code": 403, 
                    "title": "Forbidden"
                }
            }, 403)


def _get_enforcer():
    return current_app.policy_enforcer
enforcer = LocalProxy(_get_enforcer)

def _get_creds():
    return _request_ctx_stack.top.creds
creds = LocalProxy(_get_creds)

