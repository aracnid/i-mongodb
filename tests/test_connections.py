"""Test connections for i_mongodb.py.
"""
from i_mongodb import MongoDBInterface


def test_close_connection(caplog):
    """Test close connection.
    """
    mdbi1 = MongoDBInterface()
    mdb1 = mdbi1.get_mdb(name='_testdb')
    assert mdb1.name == '_testdb'
    assert 'Starting topology monitoring' in caplog.records[0].message

    mdbi1.disconnect()

    mdbi2 = MongoDBInterface()
    mdb2 = mdbi2.get_mdb(name='admin')
    assert mdb2.name == 'admin'
    assert 'Topology description changed' in caplog.records[1].message

    mdbi2.disconnect()

def test_multiple_connections(caplog):
    """Test if multiple objects use the same connection.
    """
    mdbi1 = MongoDBInterface()
    mdb1 = mdbi1.get_mdb(name='_testdb')
    assert mdb1.name == '_testdb'
    assert 'Starting topology monitoring' in caplog.records[0].message

    mdbi2 = MongoDBInterface()
    mdb2 = mdbi2.get_mdb(name='admin')
    assert mdb2.name == 'admin'
    assert 'Topology description changed' in caplog.records[1].message
