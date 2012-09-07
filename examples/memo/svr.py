from multiprocessing.connection import Listener


listener = Listener(('127.0.0.1', 5555), authkey='foo')

connection = listener.accept()
while True:
    print connection.recv()
    connection.send('pong')
