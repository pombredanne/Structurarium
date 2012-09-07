from properties import BaseProperty, Identifier


class Reference(Identifier):

    def __init__(self, vertex_class, collection=None, related_collection=None):
        self._vertex_class = vertex_class
        self.graph = None
        self.name = None
        self.collection = collection
        self.related_collection = related_collection
        super(Reference, self).__init__()

    @property
    def vertex_class(self):
        if not isinstance(self._vertex_class, type):
            # it is a string
            klass = self.graph.elements_classes[self._vertex_class]
            self._vertex_class = klass
        return self._vertex_class

    def __get__(self, object, cls=None):
        if object is None:
            return self
        value = object.values[self].value
        if isinstance(value, basestring):
            # it isn't a Vertex instance
            value = self.vertex_class.graph.get(value).object()
            object.values[self].value = value
            return value
        else:
            return value

    def modified(self, object):
        new = getattr(object, self.name)

        if not isinstance(new, basestring):
            return new.modified()
        else:
            return False


class ReferenceList(BaseProperty):

    initial_value = set

    def __set__(self, object, cls):
        raise Exception('Impossible to set this way, create an edge instead.')
