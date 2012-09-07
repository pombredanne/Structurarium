import os
import copy
from random import choice

from structurarium.exceptions import ElementNotFound
from structurarium.exceptions import InvalidConcurrentTransaction

from structurarium.utils import loads
from structurarium.utils import dumps
from structurarium.utils import generate_identifier

from document import Document


ASCEND = 1
DESCEND = 2

CREATION = '_c'
EXPIRE = '_e'
NEXT = '_n'
PREVIOUS = '_p'


class MVCCDocument(Document):
    """Base class for mvcc documents."""

    __debug_attrs__ = (
        'txn',
        'identifier',
        'version',
        'modified',
        'value'
    )

    def __init__(self, txn, identifier, version, value):
        super(MVCCDocument, self).__init__(txn, identifier, value)
        self.version = version
        self.deleted_version = False
        self.new = False

    def creation_ts(self, set=False):
        """Get the write timestamp of the document, if ``set`` is ``True``
        the transaction timestamp is set"""
        if set:
            self.set(CREATION, self.txn.ts())
        return self.get(CREATION, None)

    def expire_ts(self, set=False):
        """Get the expired timestamp of the document, if ``set`` is ``True``
        the transaction timestamp is set"""
        if set:
            self.set(EXPIRE, self.txn.ts())
        return self.get(EXPIRE, None)

    # FIXME: for now we comsume database space and use random version numbers
    # that's I think we need both forward and backtracking instead the random
    # access of os.listdir. We might test if ascend identifiers make things
    # easier in this part of the db and doesn't slow down anything.

    # forward link is used to keep track of growing
    # version identifiers
    def _get_next(self):
        return self.get(NEXT, None)

    def _set_next(self, version):
        if not version and NEXT in self.value:
            self.value.pop(NEXT)
            self.modified = True
        elif not version:
            pass
        else:
            self.set(NEXT, version)

    next = property(_get_next, _set_next)

    # backward link is used to keep track of descending
    # version identifiers
    def _get_prev(self):
        return self.get(PREVIOUS, None)

    def _set_prev(self, version):
        self.set(PREVIOUS, version)

    previous = property(_get_prev, _set_prev)

    @classmethod
    def create(cls, txn, value=None):
        identifier = generate_identifier()
        version = generate_identifier()
        element = cls(txn, identifier, version, value)
        element.creation_ts(True)
        element.modified = True
        element.new = True
        txn.elements[element.identifier] = element
        return element

    @classmethod
    def load(cls, txn, identifier):
        # try to load from transaction if it exists
        if identifier in txn.elements:
            return txn.elements[identifier]
        # we cannot load from cache since it might not be a good version
        # of the element

        path = os.path.join(txn.database.path(), cls.directory(), identifier)
        if not os.path.exists(path):
            raise ElementNotFound(cls, identifier)

        # max_element will be the elected element, if at the end of the
        # election algorithm max_element is still min_element then the
        # requested element does not exist
        version = choice(os.listdir(path))
        # initial direction is ascend because we want the highest
        # version
        while True:
            if version in txn.database.cache:
                element = txn.database.cache[version].copy()
            else:
                with open(os.path.join(path, version), 'rb') as f:
                    value = loads(f.read())
                element = cls(txn, identifier, version, value)
            # Since we still don't know if the element will be edited
            # we can only load a valid element for the transaction which
            # means the latest element with a valid ts. A valid ts means
            # that the associated transaction is commited and wasn't started
            # at the beggining of this transaction.
            if txn.is_commited(element.creation_ts()):
                expired_at = element.expire_ts()
                if expired_at and txn.is_commited(expired_at):
                    version = element.next
                    if version:
                        continue
                    else:
                        raise ElementNotFound(cls, identifier)
                else:
                    break
            else:
                version = element.previous
                if version:
                    continue
                else:
                    raise ElementNotFound(cls, identifier)

        # if the cache has already the element it will increase its hit count
        txn.database.cache[element.version] = element
        txn.elements[element.identifier] = element
        return element

    def _write(self):
        path = self.path()
        if self.new:
            os.mkdir(path)
        f = open(os.path.join(path, self.version), 'wb')
        f.write(dumps(self.value))
        f.flush()
        os.fsync(f.fileno())
        f.close()

    def save(self):
        if self.modified:  # we only need to write on disk if the object
                           # was modified
            if not self.next:  # the version was/is a valid version
                               # for a write
                version = generate_identifier()
                previous = self.copy()
                copy = previous.copy()
                previous.next = version
                previous.expire_ts(True)
                # we still have the monopoly on the value of the element
                in_cache = copy.version in self.txn.database.cache
                if (in_cache and self.txn.database.cache.check_and_set(
                        copy.version,
                        copy,
                        previous
                    ) or not in_cache):
                    if in_cache:
                        # it's not a creation we need to edit
                        # old version to link to the new version
                        previous._write()
                        self.previous = previous.version
                    self.version = version
                    self.next = None
                    self._write()
                    # checkout this new version in the cache
                    self.txn.database.cache[self.version] = self
                else:
                    raise InvalidConcurrentTransaction
            else:
                # The problem with this is that we do all the commands in
                # the txn before invalidating it.
                raise InvalidConcurrentTransaction

    def delete(self):
        """Delete version on disk"""
        os.remove(os.path.join(self.path(), self.version))
        self.modified = True
        self.deleted_version = True

    def copy(self):
        cls = type(self)
        value = copy.deepcopy(self.value)
        new = cls(self.txn, self.identifier, self.version, value)
        return new

    @classmethod
    def iter(cls, txn):
        path = os.path.join(txn.database.path(), cls.directory())
        for identifier in os.listdir(path):
            yield cls.load(txn, identifier)
