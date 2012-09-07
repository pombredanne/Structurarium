from sys import maxint

from utils import write


class Value(object):

    def __init__(self, memo, key, value):
        super(Value, self).__init__(memo, key)
        self.value = value

    # COMMANDS

    @staticmethod
    @write
    def SET(memo, *args):
        key = args[1]
        args = args[2:]
        memo.dict[key] = Value(memo, key, *args)
        return 'RESULT', 'OK'

    def GET(self):
        return 'RESULT', self.value
