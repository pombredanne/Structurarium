from time import mktime
from datetime import datetime


class PropertyValue(object):
    """Value of a property in an element"""

    def __init__(self, value=None):
        self.value = value
        #: Track element updates, a modification a the value on a new
        #: object does not trigger an update but a save.
        self.update = False


class BaseProperty(object):
    """Base class data-descriptor for element properties. Subclass
    it to implement new types. Most likely youwill need to implement
    :meth:`unwrap` and :meth:`wrap`. Several property for the same
    python type are not supported.
    """
    initial_value = lambda x: None

    def __init__(self, default=None):
        # both are set by metaclass
        self.graph = None
        self.name = None
        self.default = None

    def __get__(self, object, cls=None):
        if not object:
            return self
        else:
            return object.values[self].value

    def __set__(self, object, value):
        if object.identifier:
            object.values[self].update = True
        object.values[self].value = value

    def __delete__(self, object):
        setattr(object, self.name, None)

    def init(self, object, value):
        value = value if value else self.initial_value()
        object.values[self] = PropertyValue(value)

    def update(self, object):
        return self.object.values[self].update

    def wrap(self, object):
        value = getattr(object, self.name)
        return value

    def unwrap(self, value):
        return value


class String(BaseProperty):
    initial_value = str


class Integer(BaseProperty):
    initial_value = int


class Boolean(BaseProperty):
    initial_value = bool

    def wrap(self):
        value = super(Boolean, self.wrap())
        return True if value else False


class Datetime(Integer):

    def __init__(self, auto_now_add=False, auto_now=False):
        super(Datetime, self).__init__()

        self.auto_now_add = auto_now_add
        self.auto_now = auto_now

    def unwrap(self, value):
        return datetime.fromtimestamp(value)

    def mktime(self, value):
        return int(mktime(value.timetuple()))

    def wrap(self, object):
        value = super(Datetime, self).wrap(object)
        if self.auto_now_add:
            if value is None:
                value = datetime.now()
                self.__set__(object, value)
        elif self.auto_now:
            value = datetime.now()
            self.__set__(object, value)
        return self.mktime(value) if value else None


class Float(BaseProperty):
    initial_value = float


class Identifier(BaseProperty):
    pass


class List(BaseProperty):
    pass


class Dict(BaseProperty):
    pass
