from itertools import chain

from structurarium.elements.mvccdocument import MVCCDocument


# these are actually metadata and not part of graph's vertex data structure
# they are referenced in vertices for optimizing queries on vertex over edges
# If the client needs to know all the edges of a vertex, she will need to query
# for them
OUTGOINGS = '_o'
INCOMINGS = '_i'


class Vertex(MVCCDocument):
    """A vertex is a document with special properties that helps
    keep track of incomings and outgoings edges

    ``add_*`` and ``remove_*`` must not be called outside of the
    :class:`Edge` class"""

    def __init__(self, txn, identifier, version, value):
        super(Vertex, self).__init__(txn, identifier, version, value)
        for edges in (OUTGOINGS, INCOMINGS):
            if edges in self.value:
                self.value[edges] = self.value[edges]

    # Add edge

    def _add_edge(self, name, edge):
        edges = self.get(name)
        if not edges:
            edges = list()
            self.set(name, edges)
        edges.append(edge.identifier)
        self.modified = True

    def add_incoming(self, edge):
        self._add_edge(INCOMINGS, edge)

    def add_outgoing(self, edge):
        self._add_edge(OUTGOINGS, edge)

    # Remove edge

    def _remove_edge(self, edges, edge):
        edges = self.get(edges)
        edges.remove(edge.identifier)
        self.modified = True

    def remove_incoming(self, edge):
        self._remove_edge(INCOMINGS, edge)

    def remove_outgoing(self, edge):
        self._remove_edge(OUTGOINGS, edge)

    # get edges

    def _edges(self, edges):
        edges = self.get(edges)
        return edges if edges else list()

    def outgoings(self):
        return self._edges(OUTGOINGS)

    def incomings(self):
        return self._edges(INCOMINGS)

    def delete(self):
        """Expires the vertex and related edges. The objects will be deleted
        from disk on next clean."""
        # fix a circular imports
        from edge import Edge

        self.expire_ts(True)
        for edge in chain(self.outgoings(), self.incomings()):
            Edge.load(edge).delete()
