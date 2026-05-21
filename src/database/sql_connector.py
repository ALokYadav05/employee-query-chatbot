from src.core import Config
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from sqlalchemy.exc import OperationalError
import logging

config = Config()


class SQLDatabaseConn:
    """ Handles MSSQL database connectivity using SQLAlchemy + pyodbc. """

    def __init__(self):
        self.connection_url = config.SQL_CONN_URL
        self.engine = None
        self.db = None

    def connect(self):
        """
        Used to connect with SQL Server Database.
        Returns: returning SQL instance.
        """
        try:
            # Create SQLAlchemy engine using connection string
            self.engine = create_engine(
                self.connection_url,
                pool_size=5,
                max_overflow=5,  # extra burst connection if pool_size limit is reached
                pool_recycle=3600,  # connection expires after 1 hour
                pool_pre_ping=True  # check if connection alive
            )

            # Create a LangChain SQLDatabase wrapper around the SQLAlchemy engine
            self.db = SQLDatabase(self.engine)
            logging.info("SQL Database connection established successfully!")
            return self.db

        except OperationalError as e:
            logging.error(f"SQL Connection Error: {e}", exc_info=True)
        except Exception as e:
            logging.error(f"SQL Connection Error: {e}", exc_info=True)

    def dispose(self):
        """
        Dispose of the engine cleanly.
        """
        try:
            if self.engine:
                # Dispose engine to release database connections
                self.engine.dispose()
        except Exception as e:
            logging.error(f"Dispose Error: {e}", exc_info=True)
