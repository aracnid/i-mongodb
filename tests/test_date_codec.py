"""Test functions for date codec.
"""
from datetime import date

import pytest

from i_mongodb import MongoDBInterface


@pytest.fixture(name='test_collection')
def fixture_mongodb_interface():
    """Pytest fixture to initialize and return the MongoDBInterface object.
    """
    mdb = MongoDBInterface().get_mdb(db_name='_testdb')
    return mdb.get_collection('_test')

def test_encode_date(test_collection):
    """Tests inserting a document with date values.
    """
    doc_write = {
        '_id': 'test_date_codec',
        'date_value': date.today()
    }

    doc_read = test_collection.find_one_and_replace(
        filter={'_id': 'test_date_codec'},
        replacement=doc_write,
        upsert=True)

    assert isinstance(doc_read['date_value'], date)

def test_decode_date(test_collection):
    """Tests retrieving a document back into date values.
    """
    doc_read = test_collection.find_one(
        filter={'_id': 'test_date_codec'}
    )

    assert doc_read
    assert isinstance(doc_read['date_value'], date)

def test_encode_string_with_isodate(test_collection):
    """Tests inserting a document with isodate embedded in other strings.

    This should be processed as a string.
    """
    doc_write = {
        '_id': 'test_str_with_iso_codec',
        'string_value': 'MASTER_Lord Fairfax English Pale Ale_2016-11-14'
    }

    doc_read = test_collection.find_one_and_replace(
        filter={'_id': 'test_str_with_iso_codec'},
        replacement=doc_write,
        upsert=True)

    assert isinstance(doc_read['string_value'], str)

def test_decode_string_with_isodate(test_collection):
    """Tests retrieving a document with isodate embedded in other strings.

    This should be processed as a string.
    """
    doc_read = test_collection.find_one(
        filter={'_id': 'test_str_with_iso_codec'}
    )

    assert doc_read
    assert isinstance(doc_read['string_value'], str)
