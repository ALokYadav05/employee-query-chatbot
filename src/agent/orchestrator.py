from langchain_ollama import ChatOllama
from src.core import config
from src.core import prompt_loader
from src.tools import retrieve_context, sql_toolkit
from langchain.agents import create_agent
import logging


class OrchestratorAgent:
    """
    Orchestrator Agent that uses Language model with SQL and RAG tools
    to answer employee related queries
    """

    def __init__(self):
        """ Initialize the agent with model and system prompt."""
        self.llm = ChatOllama(
            model=config.GEMMA_CLOUD_MODEL,
            temperature=0.3,
            # base_url=config.BASE_URL
        )
        self.prompt = prompt_loader.load_prompt()
        self.agent = None

    def create_agent(self):
        """
        Create the agent with tools and system prompt.
        """
        try:
            self.agent = create_agent(
                model=self.llm,
                tools=[retrieve_context, sql_toolkit],
                system_prompt=self.prompt
            )
            logging.info("Agent created successfully!")
        except Exception as e:
            logging.error(f"Error while creating agent: {e}", exc_info=True)

    def run_query(self, query: str):
        """
        Run a user query and stream the agent's response.
        """
        try:
            self.create_agent()
            for event in self.agent.stream(
                    {"messages": [{"role": "user", "content": query}]}
            ):
                result = event["messages"][-1].pretty_print()
                return result

            logging.info("Agent ran successfully!")

        except Exception as e:
            logging.error(f"Error while running query: {e}", exc_info=True)


agent = OrchestratorAgent()
