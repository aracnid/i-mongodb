"""Test functions for date codec.
"""
from datetime import date

import pytest

import i_mongodb as imdb

# initialize module variables
DB_NAME = '_testdb'


@pytest.fixture(name='mdb')
def fixture_mongodb_interface():
    """Pytest fixture to initialize and return the MongoDBInterface object.
    """
    return imdb.MongoDBInterface(db_name=DB_NAME)

def test_encode_date(mdb):
    """Tests inserting a document with date values.
    """
    doc_write = {
        '_id': 'test_date',
        'date_value': date.today()
    }

    doc_read = mdb._test.find_one_and_replace(
        filter={'_id': 'test_date'},
        replacement=doc_write,
        upsert=True)

    assert type(doc_read['date_value']) is date


def test_decode_decimal(mdb):
    """Tests retrieving a document back into date values.
    """
    doc_read = mdb._test.find_one(
        filter={'_id': 'test_date'}
    )

    assert doc_read
    assert type(doc_read['date_value']) is date
