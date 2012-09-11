from multiprocessing.connection import Client
from multiprocessing.connection import answer_challenge

from fondant.datastructures import DictList

from elements import Edge
from elements import Vertex

from properties import String
from properties import Integer
from properties import Boolean
from properties import Float
from properties import List
from properties import Dict
from properties import Datetime
from properties import Reference

from exception import DatabaseException
from orm_query import ORMQuery


class Graph(object):
    """A graph database. Every elements that are found in this graph should
    reference it as ``graph`` class attribute, see :class:`graphiti.elements
    Vertex`` & :class:`graphiti.elements.Edge``."""

    EdgeClass = Edge
    VertexClass = Vertex
    ORMQueryClass = ORMQuery

    Reference = Reference
    DateTime = Datetime
    Integer = Integer
    Boolean = Boolean
    String = String
    Float = Float
    List = List
    Dict = Dict

    def __init__(self, authkey=None, address=('127.0.0.1', 8000)):
        self.address = address

        self.elements_classes = dict()

        self.references = DictList()

        class GraphORMQuery(self.ORMQueryClass):
            pass

        self.ORMQuery = GraphORMQuery
        self.ORMQuery.graph = self

        class GraphEdge(self.EdgeClass):
            pass
        self.Edge = GraphEdge
        self.Edge.graph = self

        class GraphVertex(self.VertexClass):
            pass
        self.Vertex = GraphVertex
        self.Vertex.graph = self

    def get(self, identifier):
        return self.query().by_identifier(identifier)

    def query(self):
        return self.ORMQuery()

    def register(self, element_class):
        self.elements_classes[element_class.__name__] = element_class
        self.query().__add_element_class__(element_class)

    def _load(self, values):
        class_name = values['klass']
        Klass = self.elements_classes[class_name]
        return Klass._load(values)

    def _query(self, message):
        connection = Client(self.address, family='AF_INET')
        connection.send(message)
        response = connection.recv()
        connection.close()
        if response['type'] == 'result':
            return response['data']
        else:
            raise DatabaseException(response['data'])
