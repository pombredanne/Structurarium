import copy

from base import Base


class Document(Base):
    """The class for key/value based elements.

    Keys must be any hashable, and values can be any Python base type. Keys
    starting with an underscore ``_`` are reserved for the document metadata
    properties.
    """

    def __init__(self, txn, identifier, value):
        super(Document, self).__init__(txn, identifier, value)
        self.value = self.value if self.value else dict()

    def get(self, key, d=None):
        """Get the value associated if ``key`` returns ``d`` if the key is not
        found"""
        return self.value.get(key, d)

    def set(self, key, value):
        """Associates ``key`` with ``value``"""
        self.modified = True
        self.value[key] = value

    def iterdata(self):
        """Iterator over the items of the document that are not metadata,
        identifier, is a bonus."""
        yield 'identifier', self.identifier
        for key in self.value.keys():
            if not key.startswith('_'):
                yield key, self.value[key]

    def copy(self):
        cls = type(self)
        value = copy.deepcopy(self.value)
        new = cls(self.txn, self.identifier, value)
        return new
