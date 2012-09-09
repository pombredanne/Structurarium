import os

from structurarium.utils import dumps
from structurarium.utils import loads


class Set(object):

    def __init__(self, name, database, lock):
        self.name = name
        self.database = database
        self.lock = lock

        # create file if it doesn't exists
        if not os.path.exists(self.path()):
            os.makedirs(self.path())

    def path(self):
        return os.path.join(self.database.path(), self.name)

    def add(self, identifier, data):
        f = open(os.path.join(self.path(), identifier), 'wb')
        f.write(dumps(data))
        f.flush()
        os.fsync(f.fileno())
        f.close()

    def pop(self, identifier=None):
        self.lock.acquire()
        if identifier:
            path = os.path.join(self.path(), identifier)
            if not os.path.exists(path):
                return None
        else:
            identifier = os.listdir(self.path())[0]
            path = os.path.join(self.path(), identifier)
        with open(path, 'rb') as f:
            data = loads(f.read())
        os.remove(path)
        self.lock.release()
        return data
