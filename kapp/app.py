# -*- coding:utf-8 -*-

import json

from flask import Flask
from flask import request, jsonify
from paste.deploy.converters import asbool


from .policy import init_policy
from . import rest


def from_paste_config(config):
    """
        convert types of value in paste-deploy config:
            true, false (case-insensitive)
            int
            float
            str for others.
    """
    new_config = {}
    for k,v in config.iteritems():
        if v.lower() in ('true', 'false'):
            new_config[k] = asbool(v)
        elif v.isdigit():
            new_config[k] = int(v)
        else:
            try:
                new_config[k] = float(v)
            except ValueError as e:
                new_config[k] = v

    return new_config


def app_factory(default, **config):
    """
        paste-deploy application factory
    """
    config = from_paste_config(config)

    app = Flask(__name__, static_url_path=None, static_folder=None)
    app.config.update(config)

    # hard coded secret key
    app.config['SECRET_KEY'] = u'\xb4eXy\xe5s@,\x0e\xd8' \
                               u'\xf3\xd9\x0f\xd01\xac[' \
                               u'\x92;<P\xc1\x1c\xbf'

    init_policy(app)
    app.register_blueprint(rest.mod, url_prefix='/api/1.0')



    @app.route(r'/test/', methods=['GET', 'POST'])
    def test():
        return 'test msg'

    @app.route(r'/test/exception/', methods=['GET', 'POST'])
    def test_exc():
        raise Exception, 'test exception msg.'


    @app.route(r'/test/dump/', methods=['GET', 'POST'])
    def test_dump():
        print 'headers:', json.dumps(dict(request.headers), indent=4)
        print 'cookies:', json.dumps(dict(request.cookies), indent=4)
        print 'query string:', json.dumps(dict(request.args), indent=4)
        print 'body:'
        print repr(request.data)
        
        return jsonify({
            'headers': dict(request.headers),
            'cookies': dict(request.cookies),
            'query_string': dict(request.args),
            'body': repr(request.data)
        })

    @app.route(r'/test/creds/', methods=['GET', 'POST'])
    def dump_creds():
        test_dump()
        from .policy import get_creds_from_request
        creds = get_creds_from_request(request)
        print json.dumps(creds, indent=4)
        return jsonify(creds)

    @app.route(r'/test/target/', methods=['GET', 'POST'])
    def dump_target():
        test_dump()
        from .policy import get_target_info
        target_info = get_target_info()
        print json.dumps(target_info, indent=4)
        return jsonify(target_info)

    @app.route(r'/test/localproxy/', methods=['GET', 'POST'])
    def dump_localproxy():
        # test_dump()
        from .policy import service_target_info, enforcer, creds
        print 'service_target_info:', service_target_info._get_current_object()
        print 'enforcer:', enforcer._get_current_object()
        print 'creds:', creds._get_current_object()
        return 'ok'

    return app



