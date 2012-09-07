class GraphitiException(Exception):
    pass


class IllegalOperation(GraphitiException):
    pass


class GremlinException(GraphitiException):
    pass

class DatabaseException(GraphitiException):
    pass
