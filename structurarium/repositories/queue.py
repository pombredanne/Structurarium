import os

from structurarium.utils import dumps
from structurarium.utils import loads


class Queue(object):

    def __init__(self, name, database, lock):
        self.name = name
        self.database = database

        # create file if it doesn't exists
        if not os.path.exists(self.path()):
            f = open(self.path(), 'wb')
            f.flush()
            os.fsync(f.fileno())
            f.close()

        self.lock = lock

    def path(self):
        return os.path.join(self.database.path(), self.name)

    def add(self, value):
        self.lock.acquire()

        f = open(self.path(), 'ab')
        f.write('%s\n' % dumps(value))
        f.flush()
        os.fsync(f.fileno())
        f.close()

        self.lock.release()

    def __iter__(self):
        with open(self.path(), 'rb') as f:
            for line in f:
                yield loads(line)
