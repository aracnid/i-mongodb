"""Test functions for i_mongodb.py to test the interface class.
"""
# pylint: disable=protected-access

import pymongo

from i_mongodb import MongoDBInterface

# initialize module variables
DB_NAME = '_testdb'


def test_init_mongodb():
    """Tests MongoDB initialization.
    """
    mdbi = MongoDBInterface()
    assert mdbi
    assert isinstance(mdbi, MongoDBInterface)

def test_get_client():
    """Test retrieving MongoDB client.
    """
    mdbi = MongoDBInterface()

    mdb_client = mdbi.get_client()
    assert mdb_client
    assert isinstance(mdb_client, pymongo.MongoClient)
    