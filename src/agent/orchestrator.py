from langchain_core.messages import AIMessageChunk, HumanMessage
from langchain_ollama import ChatOllama
from src.core import config
from src.core import prompt_loader
from src.tools import rag_tool, sql_tool
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
            model=config.MISTRAL_NEMO,
            temperature=0.3,
            base_url=config.BASE_URL
        )
        self.prompt = prompt_loader.load_prompt()
        self.agent = self.create_agent()

    def create_agent(self):
        """
        Create the agent with tools and system prompt.
        """
        try:
            self.agent = create_agent(
                model=self.llm,
                tools=[rag_tool, sql_tool],
                system_prompt=self.prompt
            )
            logging.info("Agent created successfully!")
            return self.agent

        except Exception as e:
            logging.error(f"Error while creating agent: {e}", exc_info=True)

    async def run_query(self, query: str):
        """"
        Sends LLM response in streaming format
        Returns: Yield chunk
        """
        try:
            input_query = [HumanMessage(content=query)]

            async for chunk, metadata in self.agent.astream(
                    input_query,
                    stream_mode="messages"
            ):
                logging.info("Everything is working!")

                if isinstance(chunk, AIMessageChunk) and chunk.content:
                    yield chunk.content
        except Exception as e:
            logging.error(f"Error in run_query: {e}", exc_info=True)


orchest_agent = OrchestratorAgent().create_agent()
