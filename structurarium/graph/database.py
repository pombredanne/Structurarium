#!/usr/bin/env python
import os
import cPickle
import argparse
import traceback

from multiprocessing import Pool
from multiprocessing import Manager
from multiprocessing.connection import Listener
from multiprocessing.reduction import reduce_connection

from structurarium import __version__
from structurarium.utils import _setproctitle
from structurarium.base import Base
from structurarium.exceptions import ElementNotFound
from structurarium.repositories.queue import Queue

from edge import Edge
from cache import Cache
from query import Query
from vertex import Vertex
from txn import Transaction


class IntegerQueue(Queue):

    def maximum(self):
        m = None
        for timestamp in self:
            m = max(m, timestamp)
        return m


class Graph(Base):

    def __init__(self, path, authkey):
        super(Graph, self).__init__(path, authkey)

        self.authkey = authkey

        manager = Manager()
        self.current_timestamps = manager.list()

        if not os.path.exists(path):
            os.mkdir(path)
        if not os.path.exists(os.path.join(path, 'Edge')):
            os.mkdir(os.path.join(path, 'Edge'))
        if not os.path.exists(os.path.join(path, 'Vertex')):
            os.mkdir(os.path.join(path, 'Vertex'))

        self.timestamps = IntegerQueue(
            'timestamps',
            self,
            manager.Lock()
        )

        self.cache = Cache()

    def load(self, txn, identifier):
        try:
            element = Vertex.load(txn, identifier)
        except ElementNotFound:
            element = Edge.load(txn, identifier)
            return element
        else:
            return element

    def process(self, connection):
        super(Graph, self).process(connection)
        query = self.recv()
        query = Query.parse(query)
        timestamps = list(self.current_timestamps)
        maximum = self.timestamps.maximum()
        txn = Transaction(
            self,
            query,
            maximum,
            timestamps,
        )
        self.current_timestamps.append(txn.ts())
        try:
            result = txn.commit()
        except Exception:
            self.send({
                'type': 'exception',
                'data': traceback.format_exc()
            })
        else:
            self.send({'type': 'result', 'data': result})
        finally:
            self.current_timestamps.remove(txn.ts())


# function to circuvent the fact that pickled objects should
# be importable
def process(database, connection):
    database.process(connection)


def main():
    _setproctitle('structurarium.graph')
    parser = argparse.ArgumentParser(description='Run Structurarium graph server')
    parser.add_argument('--version', '-v', action='version', version=__version__)
    parser.add_argument('host')
    parser.add_argument('port', type=int)
    parser.add_argument('path')
    parser.add_argument('--authkey', '-k', action='store')
    parser.add_argument(
        '--worker',
        '-w',
        action='store',
        type=int,
        help='default is set to the number of CPU'
    )
    args = parser.parse_args()
    listener = Listener((args.host, args.port), family='AF_INET')
    database = Graph(args.path, authkey=args.authkey)
    pool = Pool(processes=args.worker)

    print 'Running on %s:%s' % (args.host, args.port)
    while True:
        connection = listener.accept()
        connection = reduce_connection(connection)
        pool.apply_async(process, [database, connection])


if __name__ == '__main__':
    main()
