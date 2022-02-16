from hive_metastore_client.builders import DatabaseBuilder
from hive_metastore_client.builders import TableBuilder
from hive_metastore_client.builders import StorageDescriptorBuilder

from hive_metastore_client import HiveMetastoreClient

if __name__ == '__main__':
    client = HiveMetastoreClient('dikehdfs', 9083).open()

    db_name = 'database1_dca'

    if db_name not in client.get_all_databases():
        print(f'Creating database {db_name}')
        database = DatabaseBuilder(name=db_name).build()
        client.create_database_if_not_exists(database)
    else:
        print(f'Database {db_name} already exists')


    # storage_descriptor = StorageDescriptorBuilder()
    # table = TableBuilder(table_name='table1', db_name='database1_dca', storage_descriptor=storage_descriptor)

    d = client.get_all_databases()
    print(d)

    client.close()


