from itertools import chain

from structurarium.utils import generate_identifier

from persistent import Persistent
from persistent.dict import PersistentDict
from persistent.list import PersistentList


INCOMINGS = '_i'
OUTGOINGS = '_o'
START = '_s'
END = '_e'


class Element(Persistent):

    @classmethod
    def name(cls):
        return cls.__name__

    def __init__(self, identifier, value, root):
        self.identifier = identifier
        self.value = value
        self.root = root

    @classmethod
    def load(cls, identifier, root):
        value = root[cls.name()][identifier]
        return cls(identifier, value, root)

    @classmethod
    def create(cls, root):
        identifier = generate_identifier()
        value = PersistentDict()
        root[cls.name()][identifier] = value
        element = cls(identifier, value, root)
        return element

    def iterdata(self):
        for key in self.value.keys():
            if not key.startswith('_'):
                yield key, self.value[key]

    def get(self, key, d):
        return self.value.get(key, d)

    def set(self, key, value):
        self.value[key] = value

    def delete(self):
        del self.root[self.name()][self.identifier]


class Vertex(Element):
    """A vertex is a document with special properties that helps
    keep track of incomings and outgoings edges

    ``add_*`` and ``remove_*`` must not be called outside of the
    :class:`Edge` class"""

    @classmethod
    def create(cls, root):
        node = super(Vertex, cls).create(root)
        node.value[OUTGOINGS] = PersistentList()
        node.value[INCOMINGS] = PersistentList()
        return node

    # Add edge

    def _add_edge(self, name, edge):
        edges = self.get(name)
        if not edges:
            edges = list()
            self.set(name, edges)
        edges.append(edge.identifier)

    def add_incoming(self, edge):
        self._add_edge(INCOMINGS, edge)

    def add_outgoing(self, edge):
        self._add_edge(OUTGOINGS, edge)

    # Remove edge

    def _remove_edge(self, edges, edge):
        edges = self.get(edges)
        edges.remove(edge.identifier)

    def remove_incoming(self, edge):
        self._remove_edge(INCOMINGS, edge)

    def remove_outgoing(self, edge):
        self._remove_edge(OUTGOINGS, edge)

    # get edges

    def _edges(self, edges):
        for identifier in self.get(edges):
            yield identifier

    def outgoings(self):
        for identifier in self._edges(OUTGOINGS):
            yield identifier

    def incomings(self):
        for identifier in self._edges(INCOMINGS):
            yield identifier

    def delete(self):
        super(Vertex, self).delete()
        for identifier in chain(self.outgoings(), self.incomings()):
            Edge.load(identifier, self.db).delete()


class Edge(Element):

    @classmethod
    def create(self, root, start, end):
        edge = super(Edge, self).create(root)
        edge.value[START] = start.identifier
        edge.value[END] = start.identifier
        return edge

    def start(self):
        return self.get(START)

    def end(self):
        return self.get(END)
