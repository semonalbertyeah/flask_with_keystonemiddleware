# -*- coding:utf-8 -*-

import signal
from waitress import serve
from werkzeug.serving import run_simple
from paste.deploy.converters import asbool

from .utils.process_util import SignalContext
from .app import from_paste_config


class Termination(BaseException):
    pass

signal_context = SignalContext()

@signal_context.on(signal.SIGTERM)
def terminate(sig, stack):
    raise Termination, "terminated by signal %d" % sig


# paste-deploy server factory
def server_factory(default, **config):
    """
        paste-deploy server factory
            return a wrapper for waitress:serve
    """
    config = from_paste_config(config)

    def serve_forever(application):
        global signal_context
        with signal_context:
            try:
                serve(application, **config)
            except (Termination, KeyboardInterrupt) as e:
                print 'end'

    return serve_forever



def server_factory_dbg(default, **config):
    """
        paste-deploy server factory
            return a server used in development environment
                -> a wrapper of werkzeug.serving:run_simple
    """
    config = from_paste_config(config)

    host = config.pop('host', '0.0.0.0')
    port = config.pop('port', 8020)

    def serve_forever(application):
        global signal_context
        with signal_context:
            try:
                run_simple(host, port, application, **config)
            except (Termination, KeyboardInterrupt) as e:
                print 'end'

    return serve_forever
