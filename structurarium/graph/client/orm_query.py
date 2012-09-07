from types import MethodType

from fondant.string import generate_instance_name

from query import Operator
from query import GraphQuery

from elements import Vertex


class ORMQuery(GraphQuery):
    """Let you query the graph in gremlin like API"""

    # FIXME: it makes impossible to have several database in the same app
    # initialised in graph.Graph
    graph = None
    element_query_class = {}

    def __add_element_class__(self, element_class):
        """Generates ``QueryVertex`` and ``QueryVertex`` for
        elements registered with the corresponding graph and
        attach them the GraphitiRexQuery class so that it's possible
        to query for this objects"""

        class_name = element_class.__name__
        element_instance_name = generate_instance_name(class_name)

        properties = element_class.properties

        # We don't need to filter by ``klass`` because that is
        # already what we do with all this stuff
        # otherwise said, we don't need automatic filtering
        # created for ``klass`` property because the purpose
        # of this code is to do exactly that

        class_dict = {}

        # both edge and vertex element classes share properties filter
        filters = {}
        for property in properties:
            if property.name == 'klass':
                continue
            def filter_by_property(self, value):
                return self.filter(property.name, value)
            method_name = generate_instance_name(property.name)
            filters[method_name] = filter_by_property
        class_dict.update(filters)

        # Build the new query class
        # inherit from the parent query class if any
        SuperClass = element_class.mro()[1]
        if SuperClass in self.element_query_class:
            bases = (self.element_query_class[SuperClass],)
        else:
            if issubclass(element_class, Vertex):
                bases = (Operator, )
            else:
                bases = (Operator, )

        query_name = '%sQuery' % class_name
        QueryKlass = type(query_name, bases, class_dict)
        QueryKlass.graph = self
        QueryKlass.element_class = element_class

        # add it to element_query_class for reference
        self.element_query_class[element_class] = QueryKlass

        # Add proper filtering on Operator base class so that it's always
        # accessible
        # FIXME: make it more fine grained because this operation must not
        # be accessible everywhere we rely on user smartness
        def filter_by_element(self, **kwargs):
            return self.filter(klass=class_name, **kwargs)
        filter_by_element = MethodType(filter_by_element, None, Operator)
        setattr(Operator, element_instance_name, filter_by_element)

        #if issubclass(element_class, Vertex):
        #    for name, property in element_class.properties.iteritems():
        #        if isinstance(property, Refernce):
        #            self.__register_reference__(name, property, element_class)

    def __iter__(self):
        # print list(self.iter())
        r = self.graph._query(self.dumps())
        return iter(r)

    def one(self):
        # print list(self.iter())
        r = self.graph._query(self.dumps())
        if not r:
            return None
        if isinstance(r, list):
            r = r[0]
        return r

    def object(self):
        r = self.properties().one()
        if r:
            return self.graph._load(r)
        else:
            return None

    def objects(self):
        for properties in self.properties():
            yield self.graph._load(properties)
