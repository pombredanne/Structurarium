class StructurariumException(Exception):
    pass


class ElementNotFound(StructurariumException):

    def __init__(self, cls, identifier):
        msg = '%s %s' % (cls.__name__, identifier)
        super(ElementNotFound, self).__init__(msg)


class InvalidConcurrentTransaction(StructurariumException):
    """The object that should be elected is actually in the middle
    of being edited, we raise this exception to retry later to write
    the file"""


class IllegalOperation(StructurariumException):
    pass
