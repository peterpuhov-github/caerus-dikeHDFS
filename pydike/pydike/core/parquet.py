import time
import threading
from fastparquet import ParquetFile
from fastparquet import core

from pydike.core.webhdfs import WebHdfsFile

reader_cache = dict()
reader_cache_lock = threading.Lock()


def get_reader(path: str):
    reader_cache_lock.acquire()
    if path not in reader_cache.keys():
        reader_cache[path] = ParquetReader(path)
    reader_cache_lock.release()

    return reader_cache[path]


class ParquetReader(ParquetFile):
    def __init__(self, path: str):
        self.infile = WebHdfsFile(path)
        super(ParquetReader, self).__init__(self.infile)
        self.infile.close()

    def read_rg(self, index: int, columns: list):
        rg = self.row_groups[index]
        #  Allocate memory
        df, assign = self.pre_allocate(rg.num_rows, columns, {}, None)

        fin = self.infile.clone()

        for col in rg.columns:
            name = col.meta_data.path_in_schema[0]
            if name in columns:
                fin.prefetch(col.meta_data.data_page_offset, col.meta_data.total_compressed_size)
                core.read_col(col, self.schema, fin, assign=assign[name])

        fin.close()
        del fin
        return df


if __name__ == '__main__':
    fname = '/tpch-test-parquet-1g/lineitem.parquet/' \
            'part-00000-badcef81-d816-44c1-b936-db91dae4c15f-c000.snappy.parquet'

    reader = ParquetReader(f'webhdfs://dikehdfs:9870/{fname}?user.name=peter')
    print(reader.columns)
    print([t.name for t in reader.dtypes.values()])
    start = time.time()
    columns = ['l_partkey', 'l_extendedprice', 'l_discount', 'l_shipdate']
    df = reader.read_rg(0, columns[:4])

    # df = reader.read_rg(0, reader.pf.columns[:])
    end = time.time()
    print(f"Run time is: {end - start:.3f} secs")
    print(df.shape)
