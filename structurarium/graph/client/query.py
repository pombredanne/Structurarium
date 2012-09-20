import os
import hashlib


def generate_identifier():
        return hashlib.md5(os.urandom(1024)).hexdigest()


class Element(object):

    def __init__(self, identifier=None):
        self._identifier = identifier if identifier else generate_identifier()
        self._data = dict()

    def debug(self):
        print "#", type(self).__name__, self._identifier
        print "## data"
        for key in self._data.keys():
            print "###", key, "=>", self._data[key]


class Vertex(Element):

    def __init__(self, identifier=None):
        super(Vertex, self).__init__(identifier)
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

    def __incomings__(self, key=None, value=None):
        return self.__edges__('incomings', key, value)

    def __outgoings__(self, key=None, value=None):
        return self.__edges__('outgoings', key, value)

    def debug(self):
        super(Vertex, self).debug()
        print "## incomings"
        for incoming in self._incomings:
            print "###", incoming
        print "## outgoings"
        for outgoing in self._outgoings:
            print "###", outgoing


class Edge(Element):

    def __init__(self, outgoing, incoming, identifier=None):
        super(Edge, self).__init__(identifier)
        self._incoming = incoming
        self._incoming._incomings.add(self)
        self._outgoing = outgoing
        self._outgoing._outgoings.add(self)

    def debug(self):
        super(Edge, self).debug()
        print "### incoming", self._incoming
        print "### outgoing", self._outgoing


class Graph(object):
    def __init__(self, identifier):
        self._identifier = identifier


class Operator(Vertex):

    def __init__(self, operation):
        super(Operator, self).__init__()
        self._data['__operation'] = operation

    def __repr__(self):
        return "<%s %s %s>" % (
            type(self).__name__,
            self._data['__operation'],
            id(self)
        )

    def iter_properties(self):
        for key in self._data:
            if not key.startswith('__'):
                yield key, self._data[key]

    def store(self, variable_name):
        operator = Operator('store')
        operator._data['__variable_name'] = variable_name
        self.graph.add_operator(operator)
        return self.graph

    def create_vertex(self):
        operator = Operator('create vertex')
        self.graph.add_operator(operator)
        return self.graph

    def create_edge(self, v1, v2):
        operator = Operator('create edge')
        operator._data['__start'] = v1
        operator._data['__end'] = v2
        self.graph.add_operator(operator)
        return self.graph

    def vertices(self, **filters):
        operator = Operator('vertices')
        self.graph.add_operator(operator)
        if filters:
            self.filter(filters)
        return self.graph

    def edges(self, **filters):
        operator = Operator('edges')
        self.graph.add_operator(operator)
        if filters:
            self.filter(filters)
        return self.graph

    def by_identifier(self, identifier):
        operator = Operator('by identifier')
        operator._data['__identifier'] = identifier
        self.graph.add_operator(operator)
        return self.graph

    def filter(self, **filters):
        operator = self.graph.last
        if not operator._data['__operation'] == 'filter':
            operator = Operator('filter')
            self.graph.add_operator(operator)
        for key, value in filters.iteritems():
            key = '__key_%s' % key
            operator._data[key] = value
        return self.graph

    def set(self, key, value):
        if key.startswith('__'):
            raise Exception('Illegal key name')
        if not self.graph.last._data['__operation'] == 'set':
            operator = Operator('set')
            self.graph.add_operator(operator)
        self.graph.last._data[key] = value
        return self.graph

    def get(self, key):
        operator = Operator('get')
        operator._data['__key'] = key
        self.graph.add_operator(operator)
        return self.graph

    def identifier(self):
        operator = Operator('identifier')
        self.graph.add_operator(operator)
        return self.graph

    def properties(self):
        operator = Operator('properties')
        self.graph.add_operator(operator)
        return self.graph

    def load(self, variable_name):
        operator = Operator('load')
        self.graph.add_operator(operator)
        operator._data['__variable_name'] = variable_name
        return self.graph

    def outgoings(self, **filters):
        operator = Operator('outgoings')
        self.graph.add_operator(operator)
        if filters:
            self.filter(filters)
        return self.graph

    def incomings(self, **filters):
        operator = Operator('incomings')
        self.graph.add_operator(operator)
        if filters:
            self.filter(filters)
        return self.graph

    def start(self, **filters):
        operator = Operator('start')
        self.graph.add_operator(operator)
        if filters:
            self.filter(filters)
        return self.graph

    def end(self, **filters):
        operator = Operator('end')
        self.graph.add_operator(operator)
        if filters:
            self.filter(filters)
        return self.graph

    def order_by(self, key, reverse=None, min=None, max=None, limit=None):
        operator = Operator('order by')
        operator._data['__key'] = key
        operator._data['__reverse'] = reverse
        operator._data['__min'] = min
        operator._data['__max'] = max
        operator._data['__limit'] = limit
        self.graph.add_operator(operator)
        return self.graph

    def delete(self):
        operator = Operator('delete')
        operator._data['__writring'] = True
        self.graph.add_operator(operator)
        return self.graph


class GraphQuery(Graph):

    def __init__(self):
        identifier = "query graph %s" % generate_identifier()
        super(GraphQuery, self).__init__(identifier)
        self.root = Operator('root')
        self.last = self.root
        self.root.graph = self

    def dumps(self):
        vertices = []
        edges = []
        elements = [self.root]
        seen = set(elements)
        while elements:
            element = elements.pop()
            data = dict(element._data)
            data['__class__'] = type(element).__name__
            data['__identifier__'] = element._identifier
            if isinstance(element, Vertex):
                vertices.append(data)
                to_add = element.__outgoings__()
            else:
                data['__incoming__'] = element._incoming._identifier
                data['__outgoing__'] = element._outgoing._identifier
                edges.append(data)
                to_add = [element._incoming]
            for element in to_add:
                if element not in seen:
                    seen.add(element)
                    elements.append(element)
        graph = {
            'vertices': vertices,
            'edges': edges,
            'identifier': self._identifier,
        }
        return graph

    def iter(self):
        operator = self.root
        yield operator
        next = operator.__outgoings__('action', 'next').next()
        while next:
            operator = next._incoming
            yield operator
            next = operator.__outgoings__('action', 'next').next()

    def __getattr__(self, attribute):
        return getattr(self.last, attribute)

    def add_operator(self, operator):
        edge = Edge(self.last, operator)
        edge._data['action'] = 'next'
        operator.graph = self
        self.last = operator

    def debug(self):
        print "Graph", self._identifier
        elements = [self.root]
        seen = set(elements)
        while elements:
            element = elements.pop()
            element.debug()
            if isinstance(element, Vertex):
                to_add = element.__outgoings__()
            else:
                to_add = [element._incoming]
            for element in to_add:
                if element not in seen:
                    seen.add(element)
                    elements.append(element)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
