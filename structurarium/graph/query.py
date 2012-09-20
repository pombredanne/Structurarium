class Element(object):

    def __init__(self, graph, identifier, data):
        self.graph = graph
        self.identifier = identifier
        self.data = data

    def debug(self):
        print "#", type(self).__name__, self.identifier
        print "## data"
        for key in self.data.keys():
            print "###", key, "=>", self.data[key]


class Vertex(Element):

    def __init__(self, graph, identifier, data):
        super(Vertex, self).__init__(graph, identifier, data)
        self._incomings = set()
        self._outgoings = set()

    def __edges__(self, direction, key=None, value=None):
        edges = getattr(self, '_%s' % direction)
        for edge in edges:
            if key:
                if key in edge.data:
                    if value:
                        if edge.data[key] == value:
                            yield edge
                    else:
                        yield edge
            else:
                yield edge

    def incomings(self, key=None, value=None):
        return self.__edges__('incomings', key, value)

    def outgoings(self, key=None, value=None):
        return self.__edges__('outgoings', key, value)

    def debug(self):
        super(Vertex, self).debug()
        # print "## incomings"
        # for incoming in self._incomings:
            # print "###", incoming.identifier #
        # print "## outgoings"
        # for outgoing in self._outgoings:
            # print "###", outgoing.identifier #

    def iter_properties(self):
        for key in self.data:
            if not key.startswith('__'):
                yield key, self.data[key]


class Edge(Element):

    def __init__(self, graph, identifier, data, outgoing, incoming):
        super(Edge, self).__init__(graph, identifier, data)
        self.incoming = incoming
        self.outgoing = outgoing

    def debug(self):
        super(Edge, self).debug()
        print "### incoming", self.incoming
        print "### outgoing", self.outgoing


class Query(object):
    def __init__(self, name):
        self.name = name
        self.elements = {}

    def debug(self):
        print "Graph", self.name
        for element in self.elements.values():
            element.debug()

    @classmethod
    def parse(cls, value):
        graph = cls(value['identifier'])
        for vertice in value['vertices']:
            identifier = vertice.pop('__identifier__')
            vertice = Vertex(graph, identifier, vertice)
            graph.elements[identifier] = vertice
            if vertice.data['__operation'] == 'root':
                graph.root = vertice
        for edge in value['edges']:
            identifier = edge.pop('__identifier__')
            outgoing = graph.elements[edge.pop('__outgoing__')]
            incoming = graph.elements[edge.pop('__incoming__')]
            edge = Edge(graph, identifier, edge, outgoing, incoming)
            outgoing._outgoings.add(edge)
            incoming._incomings.add(edge)
        return graph

    def iter(self):
        operator = self.root
        yield operator
        next = operator.outgoings('action', 'next').next()
        while next:
            operator = next.incoming
            yield operator
            next = operator.outgoings('action', 'next').next()
