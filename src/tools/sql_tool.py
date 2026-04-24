from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.tools import tool
from src.database import SQL_DB
from langchain_ollama import ChatOllama
from src.core import config

class SQLToolkit:
    """ Exposes SQL tools for orchestrator use """
    def __init__(self):
        try:
            self.db = SQL_DB.connect()

            self.llm = ChatOllama(
                            model= config.GEMMA_CLOUD_MODEL,
                            temperature=0.2,
                            # base_url=config.BASE_URL
                        )
            self.toolkit = SQLDatabaseToolkit(
                db = self.db,
                llm = self.llm
            )

            self.tools = {t.name:t for t in self.toolkit.get_tools()}

        except Exception as e:
            print(f"SQL-Tool Initialization Error: {e}")

    def query_generator_checker(self, question:str):
        """
        Generate SQL from natural language and validate it.
        Returns: generated query
        """
        try:
            # generate SQL directly from LLM
            sql_query = self.llm.invoke(question).content

            # validate SQL
            checked_query = self.tools["sql_db_query_checker"].invoke(sql_query)
            return checked_query

        except Exception as e:
            print(f"SQL Generation Error : {e}")

    def query_executor(self, sql_query:str):
        """
        Execute SQL query and return results.
        Returns: Executed SQL query
        """
        try:
            result = self.tools["sql_db_query"].invoke(sql_query)
            return result
        except Exception as e:
            print(f"SQL Execution Error : {e}")

    def get_tool(self):
        """
        Wrapper method for SQL tool named query_tool.
        Returns: langchain SQL tool
        """
        @tool("query_tool", description="Generate, validate, and execute SQL queries from NLP question.")
        def query_tool(question:str) -> str:
            checked_query = self.query_generator_checker(question)
            return self.query_executor(checked_query)
        return query_tool

sql_toolkit = SQLToolkit().get_tool()