from structurarium.utils import generate_timestamp
from structurarium.exceptions import InvalidConcurrentTransaction

from processing import process


class Transaction(object):

    def __init__(self, database, query, maximum_timestamp, current_timestamps):
        self._ts = generate_timestamp()
        self.database = database
        self.query = query
        self.maximum_timestamp = maximum_timestamp
        self.current_timestamps = current_timestamps
        self.elements = dict()

    def ts(self):
        return self._ts

    def is_commited(self, timestamp):
        s = timestamp <= self.maximum_timestamp
        s = s and (timestamp not in self.current_timestamps)
        return s

    def save(self):
        retry = 0
        while True:
            try:
                while self.elements:
                    identifier = self.elements.iterkeys().next()
                    element = self.elements.pop(identifier)
                    element.save()
            except InvalidConcurrentTransaction:
                retry += 1
                if retry > 10:
                    raise InvalidConcurrentTransaction
            else:
                break

    def commit(self):
        result = process(self)
        self.save()
        self.database.timestamps.add(self.ts())
        return result
