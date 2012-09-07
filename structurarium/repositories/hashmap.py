from structurarium.elements.base import Base

from structurarium.exceptions import ElementNotFound


class HashMap(object):

    def __init__(self, database, name):
        self.name = name
        self.database = database

        class HashMapElement(Base):

            def directory(self):
                return name

            @classmethod
            def key(self, identifier):
                return '%s%s' % (name, identifier)

            @classmethod
            def create(cls, txn, identifier, value):
                element = cls(txn, identifier, value)
                txn.add(element)
                return element

        self.HashMapElement = HashMapElement

    def insert(self, txn, key, value):
        try:
            element = self.HashMapElement.load(key)
        except ElementNotFound:
            element = self.HashMapElement.create(txn, key, value)
        else:
            element.set(value)

    def delete(self, txn, key):
        element = self.HashMapElement.load(key)
        element.delete()
