"""
Provides elements class :class:`graphiti.elements.Vertex` and
:class:`graphiti.elements.Edge`.
"""
from itertools import chain

from fondant.string import generate_instance_name

from properties import BaseProperty, Identifier, String, ReferenceList

from utils import generate_tmp_identifier


class ElementMeta(type):
    """Metaclass for element classes"""

    def __init__(klass, classname, bases, class_dict):
        """Register elements properties by looking up in the class
        mro via dir for :class:`graphiti.properties.base.BaseProperty`
        instances in ``properties`` and then in the class. Takes care of
        registring elements classes in the graph there are defined for.
        """
        klass.properties = []

        if hasattr(klass, 'graph') and not klass.abstract():
            # register properties defined in this class
            for name in dir(klass):
                property = getattr(klass, name)
                if isinstance(property, BaseProperty):
                    klass.properties.append(property)
                    property.graph = klass.graph
                    property.name = name
            klass.graph.register(klass)


class Element(object):

    __metaclass__ = ElementMeta

    identifier = Identifier()
    klass = String()

    @classmethod
    def get_or_create(cls, **filters):
        query = cls.all()
        query.filter(**filters)
        object = query.object()
        if object:
            return False, object
        object = cls(**filters)
        return True, object

    @classmethod
    def abstract(cls):
        return cls.__name__.startswith('Abstract')

    def __init__(self, **kwargs):
        kwargs['klass'] = type(self).__name__
        self.values = {}

        for property in self.properties:
            value = kwargs.get(property.name, None)
            property.init(self, value)

        # used to track element identifier during transaction
        self._tmp_identifier = None

    def query(self):
        return self.graph.query().by_identifier(self.identifier)

    def wrap(self):
        values = {}
        for property in self.properties:
            if property.name in ('outgoings', 'incomings', 'start', 'end'):
                # they can not be set or unset this way
                continue
            value = property.wrap(self)
            update = self.values[property].update
            values[property.name] = (value, update)
        return values

    @classmethod
    def _load(cls, values):
        kwargs = dict()
        for property in cls.properties:
            value = property.unwrap(values.get(property.name, None))
            kwargs[property.name] = value
        return cls(**kwargs)

    def new(self):
        return self.identifier is None

    def modified(self):
        for value in self.values.itervalues():
            if value['new']:
                return True
        return False

    def saving(self):
        return self._tmp_identifier

    def update(self, **kwargs):
        for name, value in kwargs.iteritems():
            setattr(self, name, value)

    def __eq__(self, other):
        if type(other) == type(self):
            if self.identifier is None and other.identifier is None:
                return False
            return self.identifier == other.identifier


class Vertex(Element):

    incomings = ReferenceList()
    outgoings = ReferenceList()

    @classmethod
    def all(cls, **filters):
        instance_name = generate_instance_name(cls.__name__)
        query = cls.graph.query().vertices()
        query = getattr(query, instance_name)(**filters)
        return query

    def delete(self):
        if self.identifier:
            query = self.graph.query().get_element(self.identifier).delete()

    def _save(self, query):
        values = self.wrap()
        identifier, update = values.pop('identifier')
        self._tmp_identifier = generate_tmp_identifier()

        ##  create or update the vertex
        create = False
        if not identifier:
            create = True
            query = query.create_vertex()
        else:
            query = query.by_identifier(self.identifier)

        for name, (value, update) in values.iteritems():
            if create or update:
                query.set(name, value)
        query.store(self._tmp_identifier)

        # save any edge if needed

        for edge in chain(self.incomings, self.outgoings):
            if not edge.saving():
                edge._save(query)

        return query

    def save(self):
        query = self.graph.query()
        query = self._save(query)
        identifier = query.load(self._tmp_identifier).identifier().one()
        self.identifier = identifier

        self.reset_state()

    def reset_state(self):
        if self._tmp_identifier:
            self._tmp_identifier = None
            for edge in chain(self.incomings, self.outgoings):
                edge.reset_state()

    def edge_add(self, name, edge):
        set = getattr(self, name)
        set.add(edge)

    def outgoings_add(self, edge):
        self.edge_add('outgoings', edge)

    def incomings_add(self, edge):
        self.edge_add('incomings', edge)


class Edge(Element):
    """No support for start and end modification you can only change
    an edge starting and ending vertex by creating a new edge"""

    def __init__(self, **kwargs):
        super(Edge, self).__init__(**kwargs)
        self.start.outgoings_add(self)
        self.end.incomings_add(self)

    @classmethod
    def all(cls, **filters):
        instance_name = generate_instance_name(cls.__name__)
        query = cls.graph.query().edges()
        query = getattr(query, instance_name)(**filters)
        return query

    def _save(self, query):
        values = self.wrap()
        identifier, update = values.pop('identifier')
        self._tmp_identifier = generate_tmp_identifier()

        ##  create or update
        create = False
        if not identifier:
            create = True

            def tmp_identifier(vertex_name, query):
                vertex = getattr(self, vertex_name)
                if vertex.new():
                    if not vertex.saving():
                        vertex._save(query)
                else:
                    # FIXME: don't need to load the object to retrieve the
                    # identifier
                    if not vertex._tmp_identifier:
                        query = query.by_identifier(vertex.identifier)
                        vertex._tmp_identifier = generate_tmp_identifier()
                        query.store(vertex._tmp_identifier)
                return vertex._tmp_identifier
            start = tmp_identifier('start', query)
            end = tmp_identifier('end', query)
            query = query.create_edge(
                start,
                end,
            )
        else:
            query = query.by_identifier(self.identifier)

        for name, (value, update) in values.iteritems():
            if create or update:
                query.set(name, value)

        self._tmp_identifier = generate_tmp_identifier()
        query.store(self._tmp_identifier)
        return query

    def save(self):
        query = self.graph.query()
        query = self._save(query)
        identifier = query.load(self._tmp_identifier).identifier().one()
        self.identifier = identifier

        self._tmp_identifier = None

    def reset_state(self):
        if self._tmp_identifier:
            self._tmp_identifier = None
            for vertex in (self.start, self.end):
                vertex.reset_state()
