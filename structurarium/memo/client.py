from types import MethodType

from multiprocessing.connection import Client

from structurarium.utils import loads
from structurarium.utils import dumps


class MemoClientException(Exception):
    pass


class MemoClient(object):

    def __init__(self, address, authkey=None):
        self.address = address
        self.authkey = authkey

    def __getattr__(self, attribute):

        def method(self, *args):
            args = list(args)
            args.insert(0, attribute)
            connection = Client(self.address, authkey=self.authkey)
            connection.send(dumps(args))
            result = loads(connection.recv())
            connection.close()
            if result[0] == 'RESULT':
                return result[1]
            else:
                raise MemoClientException(result[1])

        return MethodType(method, self, type(self))
