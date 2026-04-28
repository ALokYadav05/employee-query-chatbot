from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.tools import tool
from src.database import SQL_DB
from langchain_ollama import ChatOllama
from src.core import config


class SQLTool:
    """
    SQL tool class to create a toolkit for SQL database interaction.
    Using SQLDatabaseToolkit and ChatOllama LLM.
    """

    def __init__(self):
        """ Initialize database connection and LLM """
        try:
            self.db = SQL_DB.connect()  # Initialize database connection

            self.llm = ChatOllama(
                model=config.OLLAMA_NLP2SQL,
                temperature=0,
                base_url = config.BASE_URL
            )
            self.toolkit = None
            self.tools = None
            self.logger = config.logger
        except Exception as e:
            self.logger.error(f"Error while initializing SQL-tool class : {e}", exc_info=True)

    def create_toolkit(self):
        """
        Used to create the toolkit for SQL database interaction
        """
        try:
            self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
            self.tools = self.toolkit.get_tools()
            self.logger.info("Successfully created toolkit!")
        except Exception as e:
            self.logger.error(f"Error while creating toolkit: {e}", exc_info=True)

    def sql_query_tool(self):
        """
        Used to run the toolkit for SQL database interaction
        """
        self.create_toolkit()

        @tool(
            "sql_query_tool",
            description="Converts natural language queries into SQL and executes them on the connected database."
        )
        def run_sql_query(query: str):
            """
            Run a natural language query against the database.
            Converts the query to SQL and returns the results
            """
            try:
                self.create_toolkit()
                sql_tools = self.tools[0]
                result = sql_tools.invoke(query)
                self.logger.info("Successfully executed SQL query!")
                return result
            except Exception as e:
                self.logger.error(f"Error while executing SQL query: {e}", exc_info=True)

        return run_sql_query


sql_tool_obj = SQLTool()
sql_toolkit = sql_tool_obj.sql_query_tool()
