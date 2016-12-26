# -*- coding:utf-8 -*-

import threading, time

def threaded(**options):
    """
        make calling of func in a new thread.
        options:
            name -> default : decorated function name
            daemon -> default : False
            start -> default : True
        Example:
            @threaded(name='test_function', start=False, daemon=True)
            def test():
                print 'test'

            t = test()
            t.start()
            t.join()
    """
    def decorator(func):
        name = options.get('name', func.__name__)
        daemon = bool(options.get('daemon', False))
        start = bool(options.get('start', True))

        assert callable(func)

        def thread_gen(*args, **kwargs):

            t = threading.Thread(
                target=func, 
                name=name,
                args=args, 
                kwargs=kwargs
            )
            t.setDaemon(daemon)
            if start:
                t.start()
                t.setName('%s-%d' % (t.name, t.ident))
            return t

        return thread_gen

    return decorator


def make_thread(target, **options):
    return threaded(**options)(target)


def wait_threads(tasks, timeout=5):
    """
        output:
            bool -> if all tasks are finished.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        if len(filter(lambda t: t.is_alive(), tasks)) == 0:
            return True

        time.sleep(0.2)

    return False


# thread safe decorator for function
def thread_safe(func):

    _thread_lock = threading.Lock()
    def new_func(*args, **kwargs):
        with _thread_lock:
            return func(*args, **kwargs)

    return new_func


# thread safe decorator for class method
def mthread_safe(method):
    def new_method(self, *args, **kwargs):
        if not hasattr(self, '_thread_lock_'):
            self._thread_lock_ = threading.Lock()
        with self._thread_lock_:
            return method(self, *args, **kwargs)
    return new_method


if __name__ == '__main__':
    print 'main thread id:', threading.current_thread().ident
    @threaded()
    def test():
        print 'sub thread id:', threading.current_thread().ident

    test_t = test()
    test_t.join()
