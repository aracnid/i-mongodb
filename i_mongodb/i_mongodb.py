"""Class module to interface with MongoDB.
"""
from datetime import date
from decimal import Decimal
import os
import re

from aracnid_logger import Logger
from bson.codec_options import CodecOptions, TypeCodec, TypeRegistry
from bson.decimal128 import Decimal128
from dateutil import tz
import pymongo

# initialize logging
logger = Logger(__name__).get_logger()


class DecimalCodec(TypeCodec):
    """Codec to transform between Python Decimal an MongoDB Decimal128.
    """
    python_type = Decimal    # the Python type acted upon by this type codec
    bson_type = Decimal128   # the BSON type acted upon by this type codec
    def transform_python(self, value):
        """Function that transforms a custom type value into a type that BSON can encode.
        """
        return Decimal128(value)

    def transform_bson(self, value):
        """Function that transforms a vanilla BSON type value into our
        custom type."""
        return value.to_decimal()

class DateCodec(TypeCodec):
    """Codec to transform between Python date and MongoDB string representation.
    """
    python_type = date    # the Python type acted upon by this type codec
    bson_type = str   # the BSON type acted upon by this type codec
    def transform_python(self, value):
        """Function that transforms a custom type value into a type that BSON can encode.
        """
        return value.isoformat()

    def transform_bson(self, value):
        """Function that transforms a vanilla BSON type value into our
        custom type."""
        if re.search(pattern=r'^\d{4}-\d{2}-\d{2}$', string=value):
            return date.fromisoformat(value)

        return value

class MongoDBInterface:
    """MongoDB interface class.

    Environment Variables:
        MONGODB_USER_TOKEN: MongoDB username and password.
        MONGODB_HOSTNAME: MongoDB host where database is running.
        MONGODB_DBNAME: Database name.

    Attributes:
        mdb: MongoDB database
        db_name: Name of the interfacing database.
        mongo_client: MongoDB client.

    Exceptions:
        DuplicateKeyError: MongoDB duplicate key error
    """

    DuplicateKeyError = pymongo.errors.DuplicateKeyError

    __connection_string = None
    __mongo_client = None
    __codec_options = None


    def __init__(self):
        """Initializes the interface with the database name.

        If no database name is supplied, the name is read from environment.

        Args:
            db_name: The name of the interfacing database.
        """
        # initialize object variables
        self.mdb = None
        self.db_name = None

        if MongoDBInterface.__mongo_client is None:
            # read environment variables
            mdb_user_token = os.environ.get('MONGODB_USER_TOKEN')
            mdb_hostname = os.environ.get('MONGODB_HOSTNAME')

            # initialize mongodb client
            MongoDBInterface.__connection_string = (
                f'mongodb+srv://{mdb_user_token}@{mdb_hostname}'
                '/?retryWrites=true')
            MongoDBInterface.get_client()

            # initialize codec options
            decimal_codec = DecimalCodec()
            date_codec = DateCodec()
            type_registry = TypeRegistry([decimal_codec, date_codec])
            MongoDBInterface.__codec_options = CodecOptions(
                tz_aware=True,
                tzinfo=tz.tzlocal(),
                type_registry=type_registry
            )

            logger.debug('established connection')

        else:
            logger.debug('already established connection')

    @staticmethod
    def get_client():
        """Return MongoDB client.

        This function will connect to the service once, if it hasn't be established.
        """
        if MongoDBInterface.__mongo_client is None:
            MongoDBInterface.__mongo_client = pymongo.MongoClient(
                host=MongoDBInterface.__connection_string
            )

        return MongoDBInterface.__mongo_client

    @staticmethod
    def get_codec_options():
        """Returns the MongoDB codec options.
        """
        return MongoDBInterface.__codec_options

    def get_mdb(self, name=None):
        """Return the database object
        """
        db_name = name
        if not db_name:
            db_name = os.environ.get('MONGODB_DBNAME')

        mdb = MongoDBDatabase(name=db_name, parent=self)

        return mdb

    def disconnect(self):
        """Disconnect from the MongoDB service.
        """
        MongoDBInterface.__mongo_client.close()
        MongoDBInterface.__mongo_client = None
        self.mdb = None
        self.db_name = None

class MongoDBDatabase:
    """MongoDB Database class.

    Environment Variables:
        MONGODB_DBNAME: Database name.

    Attributes:
        mdb: MongoDB database
        db_name: Name of the interfacing database.
        mongo_client: MongoDB client.

    Exceptions:
        DuplicateKeyError: MongoDB duplicate key error
    """
    def __init__(self, name: str, parent: MongoDBInterface):
        """Initializes the database with the interface and database name.

        Args:
            name: The name of the database.
            parent: MongoDBInterface object
        """
        # initialize object variables
        self.name = name
        self._interface = parent

        self._mdb = None
        if self._name:
            self._mdb = pymongo.database.Database(
                client=self._interface.get_client(),
                name=self._name,
                codec_options=self._interface.get_codec_options()
            )

    @property
    def name(self):
        """Returns the name of the database.

        Returns:
            Name of the database.
        """
        return self._name

    @name.setter
    def name(self, name):
        """Stores the name of the database.

        Args:
            name: Name of the database.
        """
        self._name = name

    @property
    def database(self):
        """Returns the MongoDB database object.
        """
        return self._mdb

    @property
    def interface(self):
        """Returns the MongoDBInterface object.
        """
        return self._interface

    def create_collection(self, name):
        """Creates and returns the specified collection.

        Args:
            name: The name of the database collection to create.

        Returns:
            The MongoDB collection object.
        """
        return self._mdb.create_collection(name=name)

    def read_collection(self, name):
        """Returns the specified collection.

        Args:
            name: The name of the database collection to return.

        Returns:
            The MongoDB collection object.
        """
        return self._mdb.get_collection(name=name)

    def delete_collection(self, name):
        """Deletes the specified collection.

        Args:
            name: The name of the database collection to delete.

        Returns:
            None
        """
        self._mdb.drop_collection(name_or_collection=name)

    def __getattr__(self, name):
        """Return the collection for the specified attribute name.
        """
        return self.read_collection(name)
