import cPickle
import argparse
from time import time

from multiprocessing import Manager
from multiprocessing import Pool
from multiprocessing.connection import Listener
from multiprocessing.reduction import reduce_connection

from structurarium import __version__

from structurarium.base import Base
from structurarium.utils import generate_identifier

from structurarium.repositories.set import Set
from structurarium.utils import MockLock
from structurarium.utils import _setproctitle
from structurarium.utils import loads
from structurarium.utils import dumps


class TaskQueue(Base):

    def __init__(self, path, authkey, worker):
        super(TaskQueue, self).__init__(path, authkey)

        if worker > 1:
            manager = Manager()
            tasks_lock = manager.Lock()
            results_lock = manager.Lock()
            self.tasks = Set('tasks', self, tasks_lock)
            self.results = Set('results', self, results_lock)
        else:
            lock = MockLock()
            self.tasks = Set('tasks', self, lock)
            self.results = Set('results', self, lock)

    def task(self):
        return self.tasks.pop()

    def add_task(self, data):
        identifier = generate_identifier()
        self.tasks.add(identifier, data)
        return identifier

    def add_result(self, identifier, data):
        data['created_at'] = time()
        self.results.add(identifier, data)

    def result(self, identifier):
        return self.results.pop(identifier)

    def process(self, connection):
        super(TaskQueue, self).process(connection)
        command = self.recv()
        action = command[0]
        if action == 'TASK':
            self.send(self.task())
        elif action == 'ADD_TASK':
            self.send(self.add_task(command[1]))
        elif action == 'ADD_RESULT':
            self.send(self.add_result(command[1], command[2]))
        elif action == 'RESULT':
            self.send(self.result(command[1]))
        else:
            raise Exception('ACTION %s NOT FOUND' % action)


# function to circuvent the fact that pickled objects should
# be importable
def process(database, connection):
    database.process(connection)


def main():
    _setproctitle('structurarium.taskqueue')
    parser = argparse.ArgumentParser(
        description='Run Structurarium graph server'
    )
    parser.add_argument(
        '--version',
        '-v',
        action='version',
        version=__version__
    )
    parser.add_argument('host')
    parser.add_argument('port', type=int)
    parser.add_argument('path')
    parser.add_argument('--authkey', '-k')
    parser.add_argument(
        '--worker',
        '-w',
        action='store',
        type=int,
        help='default is set to the number of CPU'
    )
    args = parser.parse_args()
    listener = Listener((args.host, args.port), family='AF_INET')
    database = TaskQueue(args.path, authkey=args.authkey)

    print 'Running on %s:%s' % (args.host, args.port)
    if args.worker > 1:
        pool = Pool(processes=args.worker)
        while True:
            pool = Pool(processes=args.worker)
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
