"""Test functions for i_mongodb.py.
"""
from decimal import Decimal

import pytest

import i_mongodb as imdb

# initialize module variables
DB_NAME = '_testdb'


@pytest.fixture(name='mdb')
def fixture_mongodb_interface():
    """Pytest fixture to initialize and return the MongoDBInterface object.
    """
    return imdb.MongoDBInterface(db_name=DB_NAME)

def test_encode_decimal(mdb):
    """Tests inserting a document with Decimal values.
    """
    doc_write = {
        '_id': 'test_decimal',
        'decimal_value': Decimal('123.456')
    }

    doc_read = mdb._test.find_one_and_replace(
        filter={'_id': 'test_decimal'},
        replacement=doc_write,
        upsert=True)

    assert type(doc_read['decimal_value']) is Decimal


def test_decode_decimal(mdb):
    """Tests retrieving a document back into Decimal values.
    """
    doc_read = mdb._test.find_one(
        filter={'_id': 'test_decimal'}
    )

    assert doc_read
    assert type(doc_read['decimal_value']) is Decimal
