import os

from ZODB import DB
from ZODB.FileStorage import FileStorage

import transaction


class Base(object):

    def __init__(self, path, authkey):
        if not os.path.exists(path):
            os.makedirs(path)
        self._path = path
        self.authkey = authkey

        path = os.path.join(path, 'graph.fs')
        self.storage = FileStorage(path)
        self.db = DB(self.storage)

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

    def open(self):
        return self.db.open()

    def close(self):
        transaction.get().abort()
        self.db.close()
        self.storage.close()
