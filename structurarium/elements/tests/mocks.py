class Cache(dict):

    def check_and_set(self, key, original, new):
        if self[key].value == original.value:
            self[key] = new
            return True
        return False


class Database(object):

    def __init__(self, cache=None):
        self.cache = cache if cache else Cache()

    def path(self):
        return '/tmp/graphiti-tests/'


class Transaction(object):

    def __init__(self, elements=None, ts=None):
        self.database = Database()
        self.elements = elements if elements else dict()
        self._ts = ts if ts else 1
        self.commited_ts = [1]

    def is_commited(self, ts):
        return ts in self.commited_ts

    def ts(self):
        return self._ts
