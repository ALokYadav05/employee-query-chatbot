from src.core import config
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from sqlalchemy.exc import OperationalError


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
            self.engine = create_engine(self.connection_url)

            # Create a LangChain SQLDatabase wrapper around the SQLAlchemy engine
            self.db = SQLDatabase(self.engine)
            print("SQL Database connection established successfully!")
            return self.db

        except OperationalError as e:
            print(f"SQL Connection Error: {e}")
        except Exception as e:
            print(f"SQL Error: {e}")

    def dispose(self):
        """
        Dispose of the engine cleanly.
        """
        try:
            if self.engine:
                self.engine.dispose()
        except Exception as e:
            print(f"Dispose Error: {e}")

SQL_DB = SQLDatabaseConn()