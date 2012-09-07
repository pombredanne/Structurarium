from time import time
from sys import maxint

from utils import write
from utils import check_alive


class Base(object):

    def __init__(self, memo, key):
        self.key = key
        self.memo = memo
        self.expiration = maxint

    @classmethod
    def name(cls):
        return cls.__name__

    @classmethod
    def init(cls, memo):
        memo.structures.append(cls)

    def expire_at(self, timestamp):
        self.expiration = timestamp

    def set_ttl(self, ttl):
        self.expiration = time() + ttl

    def get_ttl(self):
        if self.alive():
            return self.expiration - time()
        else:
            return None

    ttl = property(get_ttl, set_ttl)

    def persist(self):
        self.expiration = maxint

    def alive(self):
        if time() > self.expiration:
            del self.memo.dict[self.key]
            return False
        return True

    @check_alive
    def TTL(self):
        return 'RESULT', self.ttl

    @write
    @check_alive
    def EXPIRE(self, seconds):
        self.ttl = seconds
        return 'RESULT', self.expiration

    @write
    @check_alive
    def EXPIREAT(self, timestamp):
        self.expire_at(timestamp)
        return 'RESULT', 'OK'

    @write
    @check_alive
    def PERSIST(self):
        self.persist()
        return 'RESULT', 'OK'
