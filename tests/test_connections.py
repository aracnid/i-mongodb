"""Test connections for i_mongodb.py.
"""
from i_mongodb import MongoDBInterface


def test_close_connection(caplog):
    """Test close connection.
    """
    mdbi1 = MongoDBInterface()
    mdbi1.get_mdb(db_name='_testdb')
    assert mdbi1.db_name == '_testdb'
    assert caplog.records[0].message == 'established connection'

    mdbi1.disconnect()
    assert mdbi1.db_name is None

    mdbi2 = MongoDBInterface()
    mdbi2.get_mdb(db_name='admin')
    assert mdbi2.db_name == 'admin'
    assert caplog.records[1].message == 'established connection'

    mdbi2.disconnect()
    assert mdbi2.db_name is None

def test_multiple_connections(caplog):
    """Test if multiple objects use the same connection.
    """
    mdbi1 = MongoDBInterface()
    mdbi1.get_mdb(db_name='_testdb')
    assert mdbi1.db_name == '_testdb'
    assert caplog.records[0].message == 'established connection'

    mdbi2 = MongoDBInterface()
    mdbi2.get_mdb(db_name='admin')
    assert mdbi2.db_name == 'admin'
    assert caplog.records[1].message == 'already established connection'
