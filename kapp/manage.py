#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
    command tools to manage web app and server.
"""

##################################
# command:
#   start   [debug|production], host, port
#   run     [debug|production], host, port
#   stop
#   status
##################################


import sys
import argparse
import time
from paste.deploy import loadserver, loadapp

from .config import CONF
from .utils.process_util import daemonized



@daemonized(
    '/var/run/kapp.pid',
    stdout='/var/log/kapp.log',
    stderr='/var/log/kapp.log'
)
def wsgi_task(app, server):
    server(app)
wsgi_daemon = wsgi_task()


def load_wsgi(config_file, app_name='main', server_name='main'):

    # specify config file for openstack components.
    global CONF
    CONF(default_config_files=[config_file])

    app = loadapp('config:%s' % config_file, name=app_name)
    server = loadserver('config:%s' % config_file, name=server_name)

    return app, server




def start_server(args):
    global wsgi_daemon
    if wsgi_daemon.running:
        print 'already running, pid: %d' % wsgi_daemon.pid
        return

    app_name = 'main'
    server_name = 'werkzeug_simple' if args.debug else 'waitress'
    app, server = load_wsgi(args.config, app_name=app_name, server_name=server_name)

    wsgi_daemon.start(app, server)
    while not wsgi_daemon.running:
        time.sleep(0.01)

    print 'running daemon, pid: %d' % wsgi_daemon.pid
    if args.debug:
        print 'debug mode'



def run_server(args):
    global wsgi_daemon

    app_name = 'main'
    server_name = 'werkzeug_simple' if args.debug else 'waitress'
    app, server = load_wsgi(args.config, app_name=app_name, server_name=server_name)

    wsgi_daemon.run(app, server)

def stop_server(args):
    global wsgi_daemon
    if wsgi_daemon.running:
        wsgi_daemon.stop()

def server_status(args):
    global wsgi_daemon
    if wsgi_daemon.running:
        print 'running'
        print 'pid: %d' % wsgi_daemon.pid
    else:
        print 'not running'

def restart_server(args):
    global wsgi_daemon
    stop_server(args)
    start_server(args)

def exe_cmd():

    # parser
    parser = argparse.ArgumentParser(description='command line tool to control kapp.')

    subparsers = parser.add_subparsers()

    parser_cmd_start = subparsers.add_parser('start', description='start as daemon')
    parser_cmd_start.add_argument('--debug', dest='debug', action='store_true')
    parser_cmd_start.add_argument('--config', dest='config', action='store', 
                                  default='/etc/kapp/config.ini', metavar='PATH')
    parser_cmd_start.set_defaults(func=start_server)

    parser_cmd_run = subparsers.add_parser('run', description='run in terminal')
    parser_cmd_run.add_argument('--debug', dest='debug', action='store_true')
    parser_cmd_run.add_argument('--config', dest='config', action='store', 
                                default='/etc/kapp/config.ini', metavar='PATH')
    parser_cmd_run.set_defaults(func=run_server)

    parser_cmd_stop = subparsers.add_parser('stop', description='stop daemon')
    parser_cmd_stop.set_defaults(func=stop_server)

    parser_cmd_status = subparsers.add_parser('status', description='daemon status')
    parser_cmd_status.set_defaults(func=server_status)

    parser_cmd_restart = subparsers.add_parser('restart', description='restart daemon')
    parser_cmd_restart.add_argument('--debug', dest='debug', action='store_true')
    parser_cmd_restart.add_argument('--config', dest='config', action='store', 
                                default='/etc/kapp/config.ini', metavar='PATH')
    parser_cmd_restart.set_defaults(func=restart_server)



    # parse
    args = parser.parse_args()
    # clear arguments (or oslo_config will parse it and generate some error.)
    sys.argv = [sys.argv[0]]
    args.func(args)

if __name__ == '__main__':
    exe_cmd()
