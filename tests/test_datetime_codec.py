"""Test functions for datetime codec.
"""
from datetime import datetime

import pytest

from i_mongodb import MongoDBInterface


@pytest.fixture(name='test_collection')
def fixture_mongodb_interface():
    """Pytest fixture to initialize and return the MongoDBInterface object.
    """
    mdb = MongoDBInterface().get_mdb(db_name='_testdb')
    return mdb.get_collection('_test')

def test_encode_datetime(test_collection):
    """Tests inserting a document with datetime values.
    """
    doc_write = {
        '_id': 'test_datetime_codec',
        'datetime_value': datetime.now()
    }

    doc_read = test_collection.find_one_and_replace(
        filter={'_id': 'test_datetime_codec'},
        replacement=doc_write,
        upsert=True)

    assert doc_read
    assert isinstance(doc_read['datetime_value'], datetime)

def test_decode_datetime(test_collection):
    """Tests retrieving a document back into datetime values.
    """
    doc_read = test_collection.find_one(
        filter={'_id': 'test_datetime_codec'}
    )

    assert doc_read
    assert isinstance(doc_read['datetime_value'], datetime)
