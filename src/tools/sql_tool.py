from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.tools import tool
from src.database import SQLDatabaseConn
from langchain_ollama import ChatOllama
from src.core import Config
import logging

config = Config()
sql_db = SQLDatabaseConn()


class SQLTool:
    """
    SQL tool class to create a toolkit for SQL database interaction.
    Using SQLDatabaseToolkit and ChatOllama LLM.
    """

    def __init__(self):
        """ Initialize database connection and LLM """
        try:
            self.db = sql_db.connect()  # Initialize database connection

            self.llm = ChatOllama(
                model=config.GEMMA_CLOUD_MODEL,
                temperature=0,
                base_url=config.BASE_URL
            )
            self.toolkit = SQLDatabaseToolkit(
                db=self.db,
                llm=self.llm
            )
            self.tools = {t.name: t for t in self.toolkit.get_tools()}
        except Exception as e:
            logging.error(f"Error while initializing SQL-tool class : {e}", exc_info=True)

    def list_tables_tool(self):
        """
        Returns a LangChain tool that retrieves all available table names from the database.
        Returns:
            function: List tables tool that returns a comma-separated string of all tables in the database.
        """

        @tool("list_table",
              description="Input is an empty string. Output is a list of all tables present in the database.")
        def list_table(query: str = ""):
            try:
                logging.info("Called list_table.")
                res = self.tools["sql_db_list_tables"].invoke(query)
                return res
            except Exception as e:
                logging.error(f"List tables error: {e}", exc_info=True)
                return f"Error listing database tables: {e}"

        return list_table

    def schema_tool(self):
        """
        Returns a LangChain tool that fetches the schema details and sample rows for specific tables.
        Returns:
            function: Schema tool that fetches the schema definition and column details for requested tables.
        """

        @tool("db_schema",
              description="Input is a comma-separated list of table names. "
                          "Output is the schema definition and sample rows for those tables. "
                          "Use this to find relevant columns before writing a query.")
        def db_schema(tables: str):
            try:
                logging.info(f"Called db_schema for tables: {tables}")
                res = self.tools["sql_db_schema"].invoke(tables)
                return res
            except Exception as e:
                logging.error(f"Schema inspection error: {e}", exc_info=True)
                return f"Error retrieving schema: {e}"

        return db_schema

    def query_checker_tool(self):
        """
        Returns a LangChain tool that validates the SQL query syntax and fixes common mistakes.
        Returns:
            function: Validator tool that checks the query syntax with an LLM and returns a clean SQL query.
        """

        @tool("query_checker",
              description="Use this tool to validate a SQL query generated from a natural language question. ")
        def query_checker(query: str):
            try:
                logging.info("Called query_checker.")
                res = self.tools["sql_db_query_checker"].invoke({"query": query})
                logging.info("Execution of query_checker completed successfully.")
                return res
            except Exception as e:
                logging.error(f"SQL Execution Error: {e}", exc_info=True)
                return f"Error validating query: {e}"

        return query_checker

    def query_executor_tool(self):
        """
        Returns a LangChain tool that converts natural language questions into SQL queries, executes them
        on the database, and returns results.
        Returns:
            function: Execution tool that runs SQL queries against the database and returns raw records.
        """

        @tool("query_executor",
              description="Input is a valid SQL SELECT query. Output is the raw text result from the database.")
        def query_executor(query: str):
            try:
                logging.info("Called query_executor.")
                res = self.tools["sql_db_query"].invoke(query)
                logging.info("Execution of query_executor completed successfully.")
                return res
            except Exception as e:
                logging.error(f"SQL Execution Error: {e}", exc_info=True)

        return query_executor
