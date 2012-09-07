import cPickle


class Base(object):

    def __init__(self, path, authkey):
        self._path = path
        self.authkey = authkey

    def path(self):
        return self._path

    def process(self, connection):
        (func, args) = connection
        self.connection = func(*args)

    def recv(self):
        return self.connection.recv()

    def send(self, message):
        self.connection.send(message)
        self.connection.close()
