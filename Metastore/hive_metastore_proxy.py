import sys
import glob
import functools

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

sys.path.append('pymetastore')

from hive_metastore import ThriftHiveMetastore


class ThriftHiveMetastoreHandler:
    def __init__(self, client):
        self.client = client

    # def __getattr__(self, attr):
    #     return getattr(self.client, attr)

    def _decorator(self, f, attr):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            res = f(*args, **kwargs)
            print(attr, args, kwargs, 'RES: ', res)
            return res

        return wrapper

    def __getattr__(self, attr):
        f = getattr(self.client, attr)
        # value = object.__getattribute__(self, 'wrapper')
        decorator = object.__getattribute__(self, '_decorator')
        return decorator(f, attr)


# Inspired by https://thrift.apache.org/tutorial/py.html
if __name__ == '__main__':
    # Make socket
    client_transport = TSocket.TSocket('dikehdfs', 9083)
    # Buffering is critical. Raw sockets are very slow
    client_transport = TTransport.TBufferedTransport(client_transport)
    # Wrap in a protocol
    client_protocol = TBinaryProtocol.TBinaryProtocol(client_transport)
    # Create a client to use the protocol encoder
    client = ThriftHiveMetastore.Client(client_protocol)
    # Connect!
    client_transport.open()

    catalogs = client.get_catalogs()
    print(catalogs)

    handler = ThriftHiveMetastoreHandler(client)
    processor = ThriftHiveMetastore.Processor(handler)
    server_transport = TSocket.TServerSocket(host='127.0.0.1', port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, server_transport, tfactory, pfactory)

    print('Starting the server...')
    server.serve()

    # Close!
    client_transport.close()



