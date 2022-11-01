"""Test functions for i_mongodb.py.
"""
# pylint: disable=protected-access

from datetime import datetime
from dateutil import tz, utils

import pymongo
import pytest

from i_mongodb import MongoDBInterface

# initialize module variables
DB_NAME = '_testdb'
DT_NAIVE = datetime(2020, 8, 24, 11, 23)
DT_UTC = utils.default_tzinfo(DT_NAIVE, tz.UTC)
DT_LOCAL = utils.default_tzinfo(DT_NAIVE, tz.tzlocal())


def test_init_mongodb():
    """Tests MongoDB initialization.
    """
    mongodb = MongoDBInterface()
    assert mongodb
    assert isinstance(mongodb, MongoDBInterface)

def test_get_client():
    """Test retrieving MongoDB client.
    """
    mongodb = MongoDBInterface()

    mdb_client = mongodb.get_client()
    assert mdb_client
    assert isinstance(mdb_client, pymongo.MongoClient)

def test_get_mdb_specifying():
    """Test retrieving MongoDB database object by specifying name.
    """
    mongodb = MongoDBInterface()
    mdb = mongodb.get_mdb(db_name=DB_NAME)
    assert mdb is not None
    assert isinstance(mdb, pymongo.database.Database)

    # verify database name
    assert mdb.name == DB_NAME

def test_get_mdb_not_specifying():
    """Test retrieving MongoDB database object when name already specified.
    """
    mongodb = MongoDBInterface()
    mdb1 = mongodb.get_mdb(db_name=DB_NAME)
    assert mdb1.name == DB_NAME

    mdb2 = mongodb.get_mdb()
    assert mdb2.name == DB_NAME

    assert mdb1 == mdb2

def test_create_collection():
    """Tests collection creation.
    """
    mongodb = MongoDBInterface()

    mdb = mongodb.get_mdb(db_name=DB_NAME)
    collection_name = '_test_create'

    # delete collection if already present
    collection_name_list = mdb.list_collection_names()
    if collection_name in collection_name_list:
        mdb[collection_name].drop()

    # verify that the collection if not present
    collection_name_list = mdb.list_collection_names()
    assert collection_name not in collection_name_list

    # create collection
    collection = mongodb.create_collection(collection_name)
    assert collection.name == collection_name

    # verify that the collection was created
    collection_name_list = mdb.list_collection_names()
    assert collection_name in collection_name_list

def test_read_collection():
    """Tests collection read.
    """
    mongodb = MongoDBInterface()
    mongodb.get_mdb(db_name=DB_NAME)

    collection_name = '_test'
    collection = mongodb.read_collection(collection_name)
    assert collection.name == collection_name

def test_read_collection_by_attr():
    """Tests collection read.
    """
    mongodb = MongoDBInterface()
    mongodb.get_mdb(db_name=DB_NAME)

    collection_name = '_test'
    collection = mongodb._test
    assert collection.name == collection_name

@pytest.fixture(name='test_collection')
def fixture_datetime_test_collection():
    """Pytest fixture to set a document with different datetime formats.

    Returns the test collection.
    """
    mongodb = MongoDBInterface()
    mongodb.get_mdb(db_name=DB_NAME)

    doc_write = {
        '_id': 'test_datetime',
        'datetime_naive': DT_NAIVE,
        'datetime_utc': DT_UTC,
        'datetime_local': DT_LOCAL
    }

    collection = mongodb.mdb['_test']
    collection.find_one_and_replace(
        filter={'_id': 'test_datetime'},
        replacement=doc_write,
        upsert=True)

    return collection

def test_read_datetime_tz_utc(test_collection):
    """Tests reading UTC datetime from MongoDB.

    UTC datetime objects stored in MongoDB are retrieved naive.
    """
    doc_read = test_collection.find_one({'_id': 'test_datetime'})
    dt_read = doc_read['datetime_utc']

    assert dt_read == DT_UTC

def test_read_datetime_tz_local(test_collection):
    """Tests reading local datetime from MongoDB.

    UTC datetime objects stored in MongoDB are retrieved naive.
    """
    doc_read = test_collection.find_one({'_id': 'test_datetime'})
    dt_read = doc_read['datetime_local']

    assert dt_read == DT_LOCAL

def test_read_datetime_tz_naive(test_collection):
    """Tests reading timezone-naive datetime from MongoDB.

    UTC datetime objects stored in MongoDB are retrieved naive.
    """
    doc_read = test_collection.find_one({'_id': 'test_datetime'})
    dt_read = doc_read['datetime_naive']

    assert dt_read == DT_UTC

def test_delete_collection():
    """Tests collection deletion.
    """
    mongodb = MongoDBInterface()
    mdb = mongodb.get_mdb(db_name=DB_NAME)

    collection_name = '_test_delete'

    # create collection if not already present
    mongodb.create_collection(collection_name)

    # verify that the collection if present
    collection_name_list = mdb.list_collection_names()
    assert collection_name in collection_name_list

    # delete the collection
    mongodb.delete_collection(collection_name)

    # verify that the collection was deleted
    collection_name_list = mdb.list_collection_names()
    assert collection_name not in collection_name_list
