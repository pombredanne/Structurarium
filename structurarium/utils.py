"""
Utils
~~~~~

Usefull functions
"""
import os
import time
import hashlib


try:
    from setproctitle import setproctitle
    def _setproctitle(title):
        setproctitle("structurarium.%s" % title)
except ImportError:
    def _setproctitle(title):
        return


try:
    import msgpack
except ImportError:
    import mspack_pure as msgpack


def generate_identifier():
    return hashlib.md5(os.urandom(1024)).hexdigest()


def generate_timestamp():
    return int(time.time() * 1000000)


def dumps(data):
    return msgpack.dumps(data)


def loads(data):
    data = msgpack.loads(data, use_list=True, encoding='utf-8')
    return data


class MockLock(object):

    def acquire(self):
        pass

    def release(self):
        pass
