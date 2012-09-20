#!/usr/bin/env python
import argparse
import traceback

from multiprocessing import Pool
from multiprocessing.connection import Listener
from multiprocessing.reduction import reduce_connection

from persistent.dict import PersistentDict
import transaction

from structurarium import __version__
from structurarium.utils import _setproctitle
from structurarium.base import Base

from processing import process

from query import Query


class Graph(Base):

    def __init__(self, path, authkey):
        super(Graph, self).__init__(path, authkey)

        cnx = self.open()
        root = cnx.root()
        if 'Vertex' not in root:
            root['Vertex'] = PersistentDict()
            root['Edge'] = PersistentDict()
            transaction.commit()

    def process(self, connection):
        super(Graph, self).process(connection)
        query = self.recv()
        query = Query.parse(query)
        cnx = self.open()
        root = cnx.root()
        try:
            result = list(process(query, root))
        except Exception:
            transaction.abort()
            cnx.close()
            self.send({
                'type': 'exception',
                'data': traceback.format_exc()
            })
        else:
            transaction.commit()
            self.send({'type': 'result', 'data': result})
            cnx.close()


# function to circuvent the fact that pickled objects should
# be importable
def connect(database, connection):
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
        # pool.apply_async(connect, [database, connection])
        connect(database, connection)

if __name__ == '__main__':
    main()
