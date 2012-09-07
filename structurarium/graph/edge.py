from structurarium.elements.mvccdocument import MVCCDocument


START = '_s'
END = '_x'


class Edge(MVCCDocument):
    """Edge class"""

    @classmethod
    def create(self, txn, start, end, value=None):
        value = value if value else dict()
        value[START] = start.identifier
        value[END] = end.identifier
        edge = super(Edge, self).create(txn, value)
        start.add_outgoing(edge)
        end.add_incoming(edge)
        return edge

    def iterdata(self):
        # we override here to be able to rename
        # start and end vertex
        for item in super(Edge, self).iterdata():
            yield item
        yield 'start', self.get(START)
        yield 'end', self.get(END)

    def start(self):
        return self.get(START)

    def end(self):
        return self.get(END)

    def delete(self):
        """Expires the edge and remove itself for related edges. The object
        will be deleted form disk on next clean"""
        from vertex import Vertex

        self.expires_ts(True)

        start = Vertex.load(self.start())
        if not start.expire_ts():
            start.remove_outgoings(self)

        end = Vertex.load(self.end())
        if not end.expire_ts():
            end.remove_incomings(self)
