"""Test functions for datetime codec.
"""
from datetime import datetime

import pytest

import i_mongodb as imdb

# initialize module variables
DB_NAME = '_testdb'


@pytest.fixture(name='mdb')
def fixture_mongodb_interface():
    """Pytest fixture to initialize and return the MongoDBInterface object.
    """
    return imdb.MongoDBInterface(db_name=DB_NAME)

def test_encode_datetime(mdb):
    """Tests inserting a document with datetime values.
    """
    doc_write = {
        '_id': 'test_datetime_codec',
        'datetime_value': datetime.now()
    }

    doc_read = mdb._test.find_one_and_replace(
        filter={'_id': 'test_datetime_codec'},
        replacement=doc_write,
        upsert=True)

    assert doc_read
    assert type(doc_read['datetime_value']) is datetime

def test_decode_datetime(mdb):
    """Tests retrieving a document back into datetime values.
    """
    doc_read = mdb._test.find_one(
        filter={'_id': 'test_datetime_codec'}
    )

    assert doc_read
    assert type(doc_read['datetime_value']) is datetime
