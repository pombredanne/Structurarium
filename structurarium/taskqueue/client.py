from types import MethodType

from multiprocessing.connection import Client

from structurarium.utils import loads
from structurarium.utils import dumps


class TaskQueueClient(object):

    def __init__(self, address, authkey=None):
        self.address = address
        self.authkey = authkey

    def TASK(self):
        return self.send_and_recv('TASK')

    def ADD_TASK(self, data):
        return self.send_and_recv('ADD_TASK', data)

    def ADD_RESULT(self, identifier, data):
        return self.send_and_recv('ADD_RESULT', identifier, data)

    def RESULT(self, identifier):
        return self.send_and_recv('RESULT', identifier)

    def send_and_recv(self, *args):
        connection = Client(self.address, authkey=self.authkey)
        connection.send(dumps(args))
        result = loads(connection.recv())
        connection.close()
        return result
