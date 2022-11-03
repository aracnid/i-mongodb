"""A set of functions to retrieve and save data into MongoDB.
"""
from importlib.metadata import version

from i_mongodb.i_mongodb import MongoDBInterface, MongoDBDatabase


__version__ = version(__package__)
