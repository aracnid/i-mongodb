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
        '_id': 'test_date_codec',
        'date_value': date.today()
    }

    doc_read = mdb._test.find_one_and_replace(
        filter={'_id': 'test_date_codec'},
        replacement=doc_write,
        upsert=True)

    assert type(doc_read['date_value']) is date

def test_decode_date(mdb):
    """Tests retrieving a document back into date values.
    """
    doc_read = mdb._test.find_one(
        filter={'_id': 'test_date_codec'}
    )

    assert doc_read
    assert type(doc_read['date_value']) is date

def test_encode_string_with_isodate(mdb):
    """Tests inserting a document with isodate embedded in other strings.

    This should be processed as a string.
    """
    doc_write = {
        '_id': 'test_str_with_iso_codec',
        'string_value': 'MASTER_Lord Fairfax English Pale Ale_2016-11-14'
    }

    doc_read = mdb._test.find_one_and_replace(
        filter={'_id': 'test_str_with_iso_codec'},
        replacement=doc_write,
        upsert=True)

    assert type(doc_read['string_value']) is str

def test_decode_string_with_isodate(mdb):
    """Tests retrieving a document with isodate embedded in other strings.

    This should be processed as a string.
    """
    doc_read = mdb._test.find_one(
        filter={'_id': 'test_str_with_iso_codec'}
    )

    assert doc_read
    assert type(doc_read['string_value']) is str
