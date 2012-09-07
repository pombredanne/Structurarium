from multiprocessing.connection import Client


client = Client(('127.0.0.1', 5555), authkey='foo')

while True:
    client.send('ping')
    print client.recv()
