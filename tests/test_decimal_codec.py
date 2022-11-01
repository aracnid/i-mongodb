"""Test functions for decimal codec.
"""
from decimal import Decimal

import pytest

from i_mongodb import MongoDBInterface


@pytest.fixture(name='test_collection')
def fixture_mongodb_interface():
    """Pytest fixture to initialize and return the MongoDBInterface object.
    """
    mdb = MongoDBInterface().get_mdb(db_name='_testdb')
    return mdb.get_collection('_test')

def test_encode_decimal(test_collection):
    """Tests inserting a document with Decimal values.
    """
    doc_write = {
        '_id': 'test_decimal_codec',
        'decimal_value': Decimal('123.456')
    }

    doc_read = test_collection.find_one_and_replace(
        filter={'_id': 'test_decimal_codec'},
        replacement=doc_write,
        upsert=True)

    assert isinstance(doc_read['decimal_value'], Decimal)


def test_decode_decimal(test_collection):
    """Tests retrieving a document back into Decimal values.
    """
    doc_read = test_collection.find_one(
        filter={'_id': 'test_decimal_codec'}
    )

    assert doc_read
    assert isinstance(doc_read['decimal_value'], Decimal)
