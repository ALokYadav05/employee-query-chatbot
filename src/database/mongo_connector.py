from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ConfigurationError
from langgraph.checkpoint.mongodb import MongoDBSaver
from src.core import config
import logging


class MongoDBConn:
    """
    MongoDB Connector
    """

    def __init__(self):
        self.url = config.MONGO_CONN_URL

        if not self.url:
            raise ValueError("MONGO_CONN_URL is Missing!")

        try:
            self.client = MongoClient(self.url)
            self.client.admin.command('ping')  # Force connection check
            self.db = self.client[config.MONGO_DB]
            self.collection = self.db[config.MONGO_COLLECTION]
            logging.info(f"Connected to MongoDB Database successfully!! : {self.db}")

        except (ConnectionFailure, ConfigurationError) as e:
            logging.error(f"Could not connect to MongoDB: {e}", exc_info=True)
        except Exception as error:
            logging.error(f"Unexpected error in MongoDB setup : {error}", exc_info=True)

    def get_saver(self):
        """ Creates MongoDBSaver Instance """
        try:
            return MongoDBSaver(
                client=self.client,
                db_name=self.db.name,
                checkpoint_collection_name=self.collection.name,
            )
        except Exception as e:
            logging.error(f"Error while MongoDBSaver: {e}", exc_info=True)


mongo_checkpointer = MongoDBConn().get_saver()
