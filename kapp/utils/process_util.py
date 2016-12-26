# -*- coding:utf-8 -*-

import os, sys
import signal

import resource
import errno


def close_all_files():
    maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[0]
    if maxfd == resource.RLIM_INFINITY:
        maxfd = 1024

    for fd in xrange(maxfd):
        try:
            os.close(fd)
        except OSError as e:
            if e.errno == errno.EBADF:
                continue
            else:
                raise


class SignalContext(object):
    """
        import signal
        sig_context = SignalContext()

        class Termination(BaseException):
            pass

        @sig_context.on(signal.SIGTERM, count=3)
        def termination(signum, stack):
            raise Termination, 'terminated'

        def main():
            import time
            try:
                with sig_context:
                    while 1:
                        print 'heartbeat'
                        time.sleep(0.5)
            except Termination as e:
                print 'end'

        if __name__ == '__main__':
            main()  # keep print heartbeat until SIGTERM
    """
    def __init__(self, signal_actions={}):
        self.sig_actions = signal_actions
        self.original_actions = None

    @property
    def active(self):
        return self.original_actions is not None

    def register(self, signum, action):
        self.sig_actions[signum] = action

    def on(self, signum):
        def decorator(func):
            self.register(signum, func)
            return func
        return decorator

    def activate(self):
        assert not self.active, 'already active'

        self.original_actions = {}
        for signum in self.sig_actions.iterkeys():
            self.original_actions[signum] = signal.getsignal(signum)

        for signum, action in self.sig_actions.iteritems():
            signal.signal(signum, action)


    def deactivate(self):
        if not self.active:
            return
        for signum, action in self.original_actions.iteritems():
            signal.signal(signum, action)

        self.original_actions = None

    def __enter__(self):
        self.activate()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.deactivate()


class Daemon(object):
    def __init__(self, pidfile, func=None, args=(), kwargs={}, stdin=os.devnull, stdout=os.devnull, stderr=os.devnull):
        self.pidfn = pidfile
        self.func = func
        self.args = list(args)
        self.kwargs = kwargs
        self.stdin_fn = stdin
        self.stdout_fn = stdout
        self.stderr_fn = stderr

    def _setup_context(self):
        close_all_files()
        os.umask(0)
        os.chdir('/')
        sys.stdin = open(self.stdin_fn, 'r')
        sys.stdout = open(self.stdout_fn, 'a', False)
        sys.stderr = open(self.stderr_fn, 'a', False)

    @property
    def pid(self):
        if not os.path.exists(self.pidfn):
            return None
        with open(self.pidfn, 'r') as f:
            try:
                return int(f.read())
            except ValueError as e:
                # pid file is broken.
                return None

    @pid.setter
    def pid(self, value):
        with open(self.pidfn, 'w') as f:
            f.write(str(value))


    def del_pid_file(self):
        if os.path.exists(self.pidfn):
            os.remove(self.pidfn)

    def run(self, *args, **kwargs):
        assert callable(self.func), 'invalid function'
        if args or kwargs:
            self.args, self.kwargs = args, kwargs
        return self.func(*self.args, **self.kwargs)

    def start(self, *args, **kwargs):
        pid = os.fork()
        assert pid >= 0, 'failed to call fork'

        if pid > 0:
            # reap first child
            os.waitpid(pid, 0)
            return

        # new session:
        #   detach from parent's session (terminal)
        #   become leader of the new session.
        #   becom leader of new process group.
        os.setsid()

        pid2 = os.fork()
        assert pid2 >= 0, 'failed to call fork secondly'
        if pid2 > 0:
            # make grandchild an orphan
            os._exit(0)

        self._setup_context()

        # here's the daemon.
        assert (self.pid is None), 'daemon is running, %d' % self.pid
        self.pid = os.getpid()
        try:
            self.run(*args, **kwargs)
        finally:
            self.del_pid_file()

        os._exit(0)

    def signal(self, sig):
        return os.kill(self.pid, sig)

    def stop(self):
        return self.signal(signal.SIGTERM)

    @property
    def running(self):
        return self.pid is not None

    def cleanup(self):
        assert not self.running(), 'daemon is running.'
        self.del_pid_file()



def daemonized(pidfile, **options):
    """
        make calling of func in a daemon
        options:
            start -> default: False
            stdin -> default: os.devnull
            stdout -> default: os.devnull
            stderr -> default: os.devnull
        Example:
            pidfile = '/var/run/test.pid'
            logfile = '/var/log/test.log'
            @daemonized(pidfile, start=False, stdout=logfile, stderr=logfile)
            def test(header, info='heartbeat'):
                import time
                while True:
                    print '%s - %s' % (header, info)
                    time.sleep(0.5)

            test_daemon = test('Head', 'running')
            test_daemon.start()
            print test_daemon.pid
            print test_daemon.running   # True
            test_daemon.stop()  # send SIGTERM
    """
    def decorator(func):
        start = bool(options.get('start', False))
        stdin = options.get('stdin', os.devnull)
        stdout = options.get('stdout', os.devnull)
        stderr = options.get('stderr', os.devnull)

        assert callable(func)

        def daemon_gen(*args, **kwargs):
            daemon = Daemon(
                pidfile, 
                func=func,
                args=args,
                kwargs=kwargs,
                stdin=stdin, 
                stdout=stdout, 
                stderr=stderr
            )

            if start:
                daemon.start()

            return daemon

        return daemon_gen

    return decorator


def make_daemon(func, pidfile, **options):
    return daemonized(pidfile, **options)(func)


if __name__ == '__main__':
    std_log = '/var/log/test.log'
    pidfn = '/var/run/test.pid'

    context = SignalContext()

    class Termination(BaseException):
        pass

    @context.on(signal.SIGTERM)
    def sigterm_handler(signum, frame):
        raise Termination, 'exit from SIGTERM'

    # def task(header, info='hearbeat'):
    #     import time
    #     with context:
    #         try:
    #             while 1:
    #                 print '%s - %s' % (header, info)
    #                 time.sleep(0.5)
    #         except Termination as e:
    #             print 'end'

    # daemon = Daemon(
    #     pidfn,
    #     # args=('head',),
    #     # kwargs={'info': 'heatbeat info'},
    #     func=task, 
    #     stdout=std_log,
    #     stderr=std_log
    # )

    @daemonized(pidfn, start=False, stdout=std_log, stderr=std_log)
    def task(header, info='hearbeat'):
        import time
        with context:
            try:
                while 1:
                    print '%s - %s' % (header, info)
                    time.sleep(0.5)
            except (Termination,KeyboardInterrupt) as e:
                print 'end'

    daemon = task()

    daemon.start('header..', info='heart beat...')
    # task()


