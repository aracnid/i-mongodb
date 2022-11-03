"""Test functions for i_mongodb.py to test the database class.
"""
# pylint: disable=protected-access

from datetime import datetime
from dateutil import tz, utils

import pytest

from i_mongodb import MongoDBInterface, MongoDBDatabase

# initialize module variables
DB_NAME = '_testdb'
DT_NAIVE = datetime(2020, 8, 24, 11, 23)
DT_UTC = utils.default_tzinfo(DT_NAIVE, tz.UTC)
DT_LOCAL = utils.default_tzinfo(DT_NAIVE, tz.tzlocal())


def test_get_mdb_specifying():
    """Test retrieving MongoDB database object by specifying name.
    """
    mdbi = MongoDBInterface()
    mdb = mdbi.get_mdb(name=DB_NAME)
    assert mdb is not None
    assert isinstance(mdb, MongoDBDatabase)

    # verify database name
    assert mdb.name == DB_NAME

def test_get_mdb_not_specifying():
    """Test retrieving MongoDB database object when name already specified.
    """
    mdbi = MongoDBInterface()
    mdb = mdbi.get_mdb()
    assert mdb.name == 'testdb'

def test_get_interface():
    """Test retrieving MongoDB interface.
    """
    mdb = MongoDBInterface().get_mdb()
    mdbi = mdb.interface

    assert isinstance(mdbi, MongoDBInterface)


def test_create_collection():
    """Tests collection creation.
    """
    mdbi = MongoDBInterface()

    mdb = mdbi.get_mdb(name=DB_NAME)
    collection_name = '_test_create'

    # delete collection if already present
    collection_name_list = mdb.database.list_collection_names()
    if collection_name in collection_name_list:
        mdb.database[collection_name].drop()

    # verify that the collection if not present
    collection_name_list = mdb.database.list_collection_names()
    assert collection_name not in collection_name_list

    # create collection
    collection = mdb.create_collection(collection_name)
    assert collection.name == collection_name

    # verify that the collection was created
    collection_name_list = mdb.database.list_collection_names()
    assert collection_name in collection_name_list

def test_read_collection():
    """Tests collection read.
    """
    mdbi = MongoDBInterface()
    mdb = mdbi.get_mdb(name=DB_NAME)

    collection_name = '_test'
    collection = mdb.read_collection(collection_name)
    assert collection.name == collection_name

def test_read_collection_by_attr():
    """Tests collection read.
    """
    mdbi = MongoDBInterface()
    mdb = mdbi.get_mdb(name=DB_NAME)

    collection_name = '_test'
    collection = mdb._test
    assert collection.name == collection_name

def test_delete_collection():
    """Tests collection deletion.
    """
    mdbi = MongoDBInterface()
    mdb = mdbi.get_mdb(name=DB_NAME)

    collection_name = '_test_delete'

    # create collection if not already present
    collection_name_list = mdb.database.list_collection_names()
    if collection_name not in collection_name_list:
        mdb.create_collection(collection_name)

    # verify that the collection if present
    collection_name_list = mdb.database.list_collection_names()
    assert collection_name in collection_name_list

    # delete the collection
    mdb.delete_collection(collection_name)

    # verify that the collection was deleted
    collection_name_list = mdb.database.list_collection_names()
    assert collection_name not in collection_name_list

@pytest.fixture(name='test_collection')
def fixture_datetime_test_collection():
    """Pytest fixture to set a document with different datetime formats.

    Returns the test collection.
    """
    mdbi = MongoDBInterface()
    mdb = mdbi.get_mdb(name=DB_NAME)

    doc_write = {
        '_id': 'test_datetime',
        'datetime_naive': DT_NAIVE,
        'datetime_utc': DT_UTC,
        'datetime_local': DT_LOCAL
    }

    collection = mdb._test
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
