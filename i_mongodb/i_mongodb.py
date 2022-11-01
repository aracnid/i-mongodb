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

            # initialize mongodb database
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

        # if db_name:
        #     self.get_mdb(db_name=db_name)

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

    def get_mdb(self, db_name=None):
        """Return the database object
        """
        if db_name:
            self.db_name = db_name
            self.mdb = None
        else:
            if not self.db_name:
                self.db_name = os.environ.get('MONGODB_DBNAME')

        if self.mdb is None:
            self.mdb = pymongo.database.Database(
                client=self.get_client(),
                name=self.db_name,
                codec_options=MongoDBInterface.__codec_options
            )

        return self.mdb

    def create_collection(self, name):
        """Creates and returns the specified collection.

        Args:
            name: The name of the database collection to create.

        Returns:
            The MongoDB collection object.
        """
        return self.mdb.create_collection(name=name)

    def read_collection(self, name):
        """Returns the specified collection.

        Args:
            name: The name of the database collection to return.

        Returns:
            The MongoDB collection object.
        """
        return self.mdb.get_collection(name=name)

    def delete_collection(self, name):
        """Deletes the specified collection.

        Args:
            name: The name of the database collection to delete.

        Returns:
            None
        """
        self.mdb.drop_collection(name_or_collection=name)

    def __getattr__(self, name):
        return self.read_collection(name)

    def disconnect(self):
        """Disconnect from the MongoDB service.
        """
        MongoDBInterface.__mongo_client.close()
        MongoDBInterface.__mongo_client = None
        self.mdb = None
        self.db_name = None
