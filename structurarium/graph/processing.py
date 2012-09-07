from sys import maxint

from edge import Edge
from vertex import Vertex


processing = dict()


def create_vertex(operator, txn, result, context):
    return [Vertex.create(txn)]
processing['create vertex'] = create_vertex


def create_edge(operator, txn, result, context):
    start = operator.data['__start']
    end = operator.data['__end']
    start = context[start][0]
    end = context[end][0]
    edge = Edge.create(txn, start, end)
    return [edge]
processing['create edge'] = create_edge


def store(operator, txn, result, context):
    variable_name = operator.data['__variable_name']
    context[variable_name] = list(result)
    return result
processing['store'] = store


def identifier(operator, txn, result, context):
    for element in result:
        yield element.identifier
processing['identifier'] = identifier


def by_identifier(operator, txn, result, context):
    identifier = operator.data['__identifier']
    element = txn.database.load(txn, identifier)
    yield element
processing['by identifier'] = by_identifier


def properties(operator, txn, result, context):
    for element in result:
        yield dict(element.iterdata())
processing['properties'] = properties


def vertices(operator, txn, result, context):
    for element in Vertex.iter(txn):
        if isinstance(element, Vertex):
            yield element
processing['vertices'] = vertices


def edges(operator, txn, result, context):
    for element in Edge.iter(txn):
        if isinstance(element, Edge):
            yield element
processing['edges'] = edges


def filter(operator, txn, result, context):
    filters = dict()
    for key, value in operator.data.iteritems():
        if key.startswith('__key_'):
            key = key[6:]
            filters[key] = value

    for element in result:
        match = True
        for key, value in filters.iteritems():
            if element.get(key, None) != value:
                match = False
                break
        if match:
            yield element
processing['filter'] = filter


def set_(operator, txn, result, context):
    for element in result:
        for key, value in operator.iter_properties():
            element.set(key, value)
        yield element
processing['set'] = set_


def get(operator, txn, result, context):
    key = operator.data['__key']
    for element in result:
        found = False
        for k, v in element.iterdata():
            if k == key:
                yield v
                found = True
                break
        if not found:
            yield None
processing['get'] = get


def outgoings(operator, txn, result, context):
    for element in result:
        for identifier in element.outgoings():
            yield txn.database.load(txn, identifier)
processing['outgoings'] = outgoings


def incomings(operator, txn, result, context):
    for element in result:
        for identifier in element.incomings():
            yield txn.database.load(txn, identifier)
processing['incomings'] = incomings


def start(operator, txn, result, context):
    for element in result:
        yield Vertex.load(txn, element.start())
processing['start'] = start


def end(operator, txn, result, context):
    for element in result:
        yield Vertex.load(txn, element.end())
processing['end'] = end


def load(operator, txn, result, context):
    variable_name = operator.data['__variable_name']
    return context[variable_name]
processing['load'] = load


def delete(operator, txn, result, context):
    for element in result:
        element.delete()
    return []
processing['delete'] = delete


def order_by(operator, txn, result, context):
    """order by:
    :key:
    :reverse:
    :min:
    :max:
    :limit:
    """
    key = operator.data['__key']
    reverse = operator.data['__reverse']
    min = operator.data['__min']
    max = operator.data['__max']
    limit = operator.data['__limit'] if operator.data['__limit'] else maxint
    result = list(result)
    result.sort(key=lambda x: x.get(key))
    i = 0
    if reverse:
        result.reverse()
    for element in result:
        if i > limit:
            break
        value = element.get(key)
        if min and (value < min):
            continue
        if max and (value >= max):
            continue
        i += 1
        yield element
processing['order by'] = order_by


def process(txn):
    # print '# PROCESSING #####################################################'
    result = set()
    context = dict()
    operators = txn.query.iter()
    operators.next()  # skip root operator
    for operator in operators:
        # operator.debug()  #
        operation = operator.data['__operation']
        operation = processing[operation]
        result = operation(operator, txn, result, context)
    return list(result)
