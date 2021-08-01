"""Test functions for i-MongoDB import.
"""
import i_mongodb

def test_version():
    """Tests that i-MongoDB was imported successfully.
    """
    assert i_mongodb.__version__
