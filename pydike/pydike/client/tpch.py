import time
import gc
import argparse
import threading
import struct
import getpass
import http.client
import json
from concurrent.futures import ThreadPoolExecutor
import urllib.parse
import numpy
import duckdb
import sqlparse
import pyarrow

from pydike.core.webhdfs import WebHdfsFile
import pydike.core.parquet as parquet
import pydike.core.util as util

class DataTypes:
    BOOLEAN = 0
    INT32 = 1
    INT64 = 2
    INT96 = 3
    FLOAT = 4
    DOUBLE = 5
    BYTE_ARRAY = 6
    FIXED_LEN_BYTE_ARRAY = 7

    type = {'int64': INT64, 'float64': DOUBLE, 'object': BYTE_ARRAY}


logging_lock = threading.Lock()

class TpchSQL:
    def __init__(self, config):
        self.df = None
        self.ndp_data = None
        self.config = config
        if config['use_ndp'] == 'True':
            self.remote_run()
        else:
            self.local_run()

    def log_message(self, msg):
        if self.config['verbose']:
            logging_lock.acquire()
            print(msg)
            logging_lock.release()

    def remote_run(self):
        url = urllib.parse.urlparse(self.config['url'])
        conn = http.client.HTTPConnection(url.netloc)
        headers = {'Content-type': 'application/json'}
        conn.request("POST", self.config['url'], json.dumps(self.config), headers)
        response = conn.getresponse()
        self.ndp_data = response.read()
        print(f'Received {len(self.ndp_data)} bytes')
        conn.close()

    def local_run(self):
        url = urllib.parse.urlparse(self.config['url'])
        fs_type = self.config['fs_type']
        if fs_type == 'webhdfs':
            reader = parquet.get_reader(f'webhdfs://{url.netloc}/{url.path}?{url.query}')
        else:
            reader = parquet.get_reader(f'file://{url.netloc}/{url.path}?{url.query}')

        tokens = sqlparse.parse(self.config['query'])[0].flatten()
        sql_columns = set([t.value for t in tokens if t.ttype in [sqlparse.tokens.Token.Name]])

        columns = [col for col in reader.columns if col in sql_columns]
        self.log_message(columns)
        rg = int(self.config['row_group'])
        df = reader.read_rg(rg, columns)
        con = duckdb.connect(database=':memory:', config={'threads': 1})

        if isinstance(df, pyarrow.lib.Table):
            con.register_arrow('arrow', df)
        else:
            con.register('arrow', df)

        con.execute(self.config['query'])
        self.df = con.fetchdf()
        con.unregister('arrow')
        con.close()

        del df
        self.log_message(f'Computed df {self.df.shape}')

    def to_spark(self, outfile):
        if self.df is None:
            outfile.write(self.ndp_data)
            return

        header = numpy.empty(len(self.df.columns) + 1, numpy.int64)
        dtypes = [DataTypes.type[self.df.dtypes[c].name] for c in self.df.columns]
        header[0] = len(self.df.columns)
        i = 1
        for t in dtypes:
            header[i] = t
            i += 1

        buffer = header.byteswap().newbyteorder().tobytes()
        outfile.write(struct.pack("!i", len(buffer)))
        outfile.write(buffer)

        for col in self.df.columns:
            self.write_column(col, outfile)

    def write_column(self, column, outfile):
        data = self.df[column].to_numpy()
        header = None
        if data.dtype == 'object' and isinstance(data[0], str):  # BYTE_ARRAY
            s = data.astype(dtype=numpy.bytes_)
            data = s.tobytes()
            data_type = DataTypes.FIXED_LEN_BYTE_ARRAY
            header = numpy.array([data_type, s.dtype.itemsize, len(data), 0], numpy.int32)
        else:  # Binary type int64, float64, etc.
            data = data.byteswap().newbyteorder().tobytes()
            data_type = DataTypes.type[self.df.dtypes[column].name]
            header = numpy.array([data_type, 0, len(data), 0], numpy.int32)

        outfile.write(header.byteswap().newbyteorder().tobytes())
        outfile.write(data)

def run_test(row_group, args):
    # fname = '/tpch-test-parquet-1g/lineitem.parquet/part-00000-badcef81-d816-44c1-b936-db91dae4c15f-c000.snappy.parquet'

    # TPC-H 100 GB
    # fname = '/tpch-test-parquet/lineitem.parquet'

    user = getpass.getuser()
    config = dict()
    config['use_ndp'] = str(args.use_ndp == 1)
    config['row_group'] = str(row_group)
    config['query'] = "SELECT l_partkey, l_extendedprice, l_discount FROM arrow WHERE l_shipdate >= '1995-09-01' AND l_shipdate < '1995-10-01';"
    config['url'] = f'http://{args.server}/{args.file}?op=SELECTCONTENT&user.name={user}&fs_type={args.fs_type}'
    config['verbose'] = args.verbose
    config['fs_type'] = args.fs_type

    return TpchSQL(config)


def get_ndp_info(args):
    user = getpass.getuser()
    conn = http.client.HTTPConnection(args.server)
    if args.fs_type != 'webhdfs':
        req = f'{args.file}?op=GETNDPINFO&user.name={user}&fs_type={args.fs_type}'
    else:
        req = f'{args.file}?op=GETNDPINFO&user.name={user}'

    conn.request("GET", req)
    resp = conn.getresponse()
    resp_data = resp.read()
    ndp_info = json.loads(resp_data)
    conn.close()
    return ndp_info

if __name__ == '__main__':
    # fname = '/data/tpch-test-parquet/lineitem.parquet/part-00000-c498f3b7-c87f-4113-8e2f-0e5e0c99ccd5-c000.snappy.parquet'
    fname = '/tpch-test-parquet/lineitem.parquet'
    
    parser = argparse.ArgumentParser(description='Run NDP server.')
    parser.add_argument('-s', '--server', default='dikehdfs:9860', help='NDP server http-address')
    parser.add_argument('-v', '--verbose', type=int, default='0', help='Verbose mode')
    parser.add_argument('-r', '--rg_count', type=int, default='1', help='Number of row groups to read')
    parser.add_argument('-n', '--use_ndp', type=int, default=1, help='Use NDP parameter')
    parser.add_argument('-f', '--file', default=fname, help='HDFS file')
    parser.add_argument('-t', '--fs_type', default='webhdfs', help='File System prefix ["webhdfs" or "localfs"')

    args = parser.parse_args()

    rg_count = args.rg_count

    if args.use_ndp == 1:
        ndp_info = get_ndp_info(args)
        for key, value in ndp_info.items():
            print(f'{key} : {value}')
    else:
        args.server = 'dikehdfs:9870'

    start = time.time()
    executor = ThreadPoolExecutor(max_workers=rg_count)
    futures = list()
    for i in range(0, rg_count):
        futures.append(executor.submit(run_test, i, args))

    res = [f.result() for f in futures]
    end = time.time()
    print(f"Query time is: {end - start:.3f} secs")
    print(f'MemUsage {util.get_memory_usage_mb()}')

# This can be used for memory consumption test
# for i in $(seq 0 300) ; do python3 /opt/volume/python3/packages/pydike/client/tpch.py -s dikehdfs:9860 -r 8 -v 1 -n 1 ; done