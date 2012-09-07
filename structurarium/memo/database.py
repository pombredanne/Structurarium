import os
import re
import argparse
import cPickle
import traceback

from random import choice
from ConfigParser import ConfigParser

from types import MethodType
from types import FunctionType

from multiprocessing import Pool
from multiprocessing import Manager
from multiprocessing.connection import Listener
from multiprocessing.reduction import reduce_connection

from structurarium import __version__
from structurarium.utils import loads
from structurarium.utils import dumps
from structurarium.utils import MockLock
from structurarium.utils import _setproctitle
from structurarium.base import Base
from structurarium.repositories.queue import Queue

from config import Config


class Memo(Base):

    def __init__(self, config):
        self.config = config
        path = config.get('memo.path', None)
        authkey = config.get('memo.authkey', None)
        super(Memo, self).__init__(path, authkey)

        self.structures = []

        manager = Manager()
        worker = self.config.getint('memo.worker', 1)

        if worker == 1:
            self.dict = dict()
        else:
            self.dict = manager.dict()

        path = config.get('memo.path', None)
        if path:
            if not os.path.exists(path):
                os.makedirs(path)
            if worker > 1:
                lock = manager.Lock()
            else:
                lock = MockLock()
            self.queue = Queue('memo.commands', self, lock)
        else:
            self.queue = None

    def add_structure(self, StructureClass):
        """Adds ``structure_class`` as an available structure in the
        instance. The structure should at least provide a staticmethod
        to initialise the key"""
        StructureClass.init(self)

        for name in dir(StructureClass):
            if name.isupper():
                attribute = getattr(StructureClass, name)
                if isinstance(attribute, FunctionType):
                    # it's staticmethod
                    key_command_method = MethodType(
                        attribute,
                        self,
                        type(self)
                    )
                    setattr(self, name, key_command_method)

    # COMMANDS

    def DEL(self, memo, *args):
        for key in args:
            if key in self.dict:
                del self.dict[key]
        return 'RESULT', 'OK'

    def EXISTS(self, memo, key):
        return 'RESULT', key in self.dict and self.dict[key].alive()

    def KEYS(self, memo, pattern=None):
        output = []
        if pattern is None:
            for key in self.dict.keys():
                if self.dict[key].alive():
                    output.append(key)
        else:
            pattern = re.compile(pattern)
            for key in self.dict.keys():
                match = pattern.match(key)
                if match is not None:
                    if key == match.group():
                        output.append(key)
        return 'RESULT', output

    def RANDOMKEY(self, memo):
        return choice(self.KEYS())

    def RENAME(self, memo, key, newkey):
        if key == newkey:
            return 'RESULT', None
        if key in self.dict:
            value = self.dict[key]
            if value.alive():
                del self.dict[key]
                self.dict[newkey] = value
                value.key = newkey
                return 'RESULT', 'OK'
        return 'ERROR', 'KEY DOES NOT EXISTS'

    def RENAMENX(self, memo, key, newkey):
        if key == newkey:
            return 'RESULT', None
        if key in self.dict:
            if newkey in self.dict:
                newkey_value = self.dict[newkey]
                if newkey_value.alive():
                    return 'ERROR', 'NEWKEY ALREADY EXISTS'
            value = self.dict[key]
            if value.alive():
                del self.dict[key]
                self.dict[newkey] = value
                value.key = newkey
                return 'RESULT', 'OK'
        return 'ERROR', 'KEY DOES NOT EXISTS'

    def STRUCTURES(self, memo):
        output = []
        for StructureClass in self.structures:
            output.append(StructureClass.name())
        return 'RESULT', output

    # internal methods

    def replay(self):
        if self.queue:
            print 'replay start'
            for command in self.queue:
                self.play(command)
            print 'replay end'

    def play(self, command):
        """Executes the command if possible and return a response
        with a flag to tell the callee whether this is a write
        operation"""
        #
        # fetch method and call it see :method:`Server._add_structure`
        #
        method = getattr(self, command[0], None)
        write = False
        if method is not None:
            write = getattr(method, 'write', False)
            if write and self.queue:
                self.queue.add(command)
            value = method(*command[1:])
            return value
        else:
            # it might be a value method
            key = command[1]
            if key in self.dict:
                value = self.dict[key]
                if not value.alive():
                    return 'ERROR', 'KEY DOES NOT EXISTS'
                method = getattr(value, command[0], None)
                if method is not None:
                    write = getattr(method, 'write', False)
                    if write and self.queue:
                        self.queue.add(command)
                    value = method(*command[2:])
                    return value
                else:
                    return 'ERROR', 'COMMAND DOES NOT EXISTS'
            return 'ERROR', 'KEY OR COMMAND DOES NOT EXISTS'

    def process(self, connection):
        super(self, Memo).process(connection)
        command = self.recv()
        try:
            result = self.play(command)
        except Exception:
            self.send('EXCEPTION', traceback.format_exc())
        else:
            self.send(result)


# function to circuvent the fact that pickled objects should
# be importable
def process(database, connection):
    database.process(connection)


def main():
    from fondant.utils import import_object

    _setproctitle('structurarium.memo')
    parser = argparse.ArgumentParser(description='Run Memo cache server')
    parser.add_argument(
        '--version', '-v', action='version', version=__version__
    )
    parser.add_argument('--host', '-o')
    parser.add_argument('--port', '-p', type=int)
    parser.add_argument('--path', '-a')
    parser.add_argument('--config', '-c')
    parser.add_argument('--authkey', '-k')
    parser.add_argument('--structure', '-s', nargs='+')
    parser.add_argument(
        '--worker',
        '-w',
        action='store',
        type=int,
        help='default is set to the number of CPU'
    )
    args = parser.parse_args()
    config = ConfigParser()
    if args.config:
        config.read(args.config)
    config = Config(args, config)
    listener = Listener(
        (config.get('memo.host'),
         config.getint('memo.port')),
         family='AF_INET',
         authkey=config.get('memo.authkey', None),
    )

    database = Memo(config)

    d = ['structures.value.Value']
    for structure_path in config.getlist('memo.structure', d):
        StructureClass = import_object(structure_path)
        database.add_structure(StructureClass)

    print 'Running on %s:%s' % (config.get('memo.host'), config.get('memo.port'))
    if config.getint('memo.worker', 1) > 1:
        while True:
            pool = Pool(processes=config.getint('memo.worker', None))
            connection = listener.accept()
            connection = cPickle.dumps(reduce_connection(connection))
            database.process(connection)
            pool.apply_async(process, [database, connection])
    else:
        print 'monothread'
        database.replay()
        while True:
            connection = listener.accept()
            command = loads(connection.recv())
            output = database.play(command)
            connection.send(dumps(output))
            connection.close()

if __name__ == '__main__':
    main()
