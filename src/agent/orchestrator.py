from langchain_core.messages import AIMessageChunk, HumanMessage
from langchain_ollama.chat_models import ChatOllama
from src.core import Config
from src.core import PromptLoader
from src.tools import RagTool, SQLTool
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware, ModelFallbackMiddleware
from langchain_core.runnables import RunnableConfig
from src.database import MongoDBConn
from typing import Literal, cast, Any
import logging

# Initialize required class
config = Config()
prompt_loader = PromptLoader()
mongo_db = MongoDBConn()
rag_tool = RagTool()
sql_tool = SQLTool()


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
        self.checkpointer = mongo_db.get_saver()
        self.agent = self.agent_creation()

    def agent_creation(self):
        """
        Create the agent with tools and system prompt.
        """
        try:
            agent = create_agent(
                model=self.llm,
                tools=[rag_tool.rag_query_tool(), sql_tool.list_tables_tool(), sql_tool.schema_tool(),
                       sql_tool.query_checker_tool(), sql_tool.query_executor_tool()],
                system_prompt=self.prompt,
                checkpointer=self.checkpointer,
                middleware=[
                    SummarizationMiddleware(
                        model=self.llm,
                        trigger=[("messages", 6)],
                        # Cast to Literal to satisfy strict type checking
                        keep=(cast(Literal["messages"], "messages"), 6)
                    ),

                    ModelFallbackMiddleware(
                        first_model=ChatOllama(
                            model=config.FALLBACK_MODEL,
                            temperature=0.3
                        )
                    )
                ]
            )
            logging.info("Agent created successfully!")
            return agent

        except Exception as e:
            logging.error(f"Error while creating agent: {e}", exc_info=True)

    async def run_query(self, query: str):
        """"
        Sends LLM response in streaming format
        Returns: Yield chunk
        """
        try:
            # Assign the result to self.agent
            if self.agent is None:
                self.agent = self.agent_creation()

            config_id: RunnableConfig = {  # type hinting to RunnableConfig
                "configurable": {
                    "thread_id": "1"
                }
            }
            input_query = cast(Any,
                               {"messages":
                                    [HumanMessage(content=query)]
                                })

            async for chunk, metadata in self.agent.astream(
                    input_query,
                    stream_mode="messages",
                    config=config_id
            ):
                logging.info("Agent is working!")

                if isinstance(chunk, AIMessageChunk) and chunk.content and metadata.get("langgraph_node") == "model":
                    yield chunk.content
        except Exception as e:
            logging.error(f"Error in run_query: {e}", exc_info=True)