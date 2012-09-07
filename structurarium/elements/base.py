import os

from structurarium.exceptions import ElementNotFound

from structurarium.utils import dumps
from structurarium.utils import loads
from structurarium.utils import generate_identifier


class Base(object):
    """Base class of all persisted elements.

    This should be subclassed with at least the :attr:`directory` property set.

      .. warning::

      The ``Base`` element doesn't deal with concurrent access to the same
      element.

    :param txn: transaction in which the element takes part.
    :param identifier: unique identifier of the element, this must be unique
                       among all the elements of the same class.
    """

    #: This is a list of class properties that we want to appear in debug
    #: see :meth:`debug`
    __debug_attrs__ = ('txn', 'identifier', 'value', 'modified')

    def __init__(self, txn, identifier, value):
        self.txn = txn
        self.identifier = identifier
        self.value = value
        self.modified = False
        # if the file is deleted no need to cache it
        self.deleted = False

    def debug(self):
        import pprint
        print type(self).__name__
        for name in self.__debug_attrs__:
            attribute = getattr(self, name)
            print name, pprint.pformat(attribute)

    def get(self, v=None):
        """Get element value"""
        return self.value if self.value else None

    def set(self, value):
        """Set element value"""
        self.modified = True
        self.value = value

    @classmethod
    def directory(cls):
        """The relative directory where are stored this elements on disk
        relative to the database directory."""
        return cls.__name__

    def path(self):
        return os.path.join(
            self.txn.database.path(),
            self.directory(),
            self.identifier,
        )

    @classmethod
    def key(cls, identifier):
        """Used to retrieve the element from cache and txn.

        The default behaviour is to use ``identifier`` as cache key, you might
        want to change that if the elements of you repository share identifiers
        with elements from other repositories of the same database."""
        return identifier

    @classmethod
    def create(cls, txn, value=None):
        """Create an object for the given transaction and with the given
        value. This method *must* register the newly created element to
        the transaction."""
        identifier = generate_identifier()
        element = cls(txn, identifier, value)
        txn.add(element)
        return element

    @classmethod
    def load(cls, txn, identifier):
        """Try to load an element of this class based on an identifier. This
        method *must* register the loaded instance to the transaction.

        If the element is not found, an :class:`ElementNotFound` exception is
        raised.
        """
        # try to load from transaction if it exists
        key = cls.key(identifier)
        if key in txn.elements:
            return txn.elements.get(key)
        # try to load from cache
        if key in txn.database.cache:
            return txn.database.cache[key]
        path = os.path.join(txn.database.path(), cls.directory(), identifier)
        if not os.path.exists(path):
            raise ElementNotFound
        with open(path, 'rb') as f:
            value = loads(f.read())
        element = cls(txn, identifier, value)
        txn.database.cache[key] = element
        txn.elements[key] = element
        return element

    def save(self):
        """Persist value on disk."""
        f = open(os.path.join(self.path()), 'wb')
        f.write(dumps(self.value))
        f.flush()
        os.fsync(f.fileno())
        f.close()

    def delete(self):
        """Remove element from disk."""
        os.remove(self.path())
        self.deleted = True
        self.modified = True
