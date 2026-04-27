from langchain_ollama import ChatOllama
from src.core import config
from src.core import prompt_loader
from src.tools import retrieve_context, sql_toolkit
from langchain.agents import create_agent

class OrchestratorAgent:
    """
    Orchestrator Agent that uses Language model with SQL and RAG tools
    to answer employee related queries
    """
    def __init__(self):
        """ Initialize the agent with model and system prompt."""
        self.llm = ChatOllama(
                            model = config.MISTRAL_NEMO,
                            temperature=0.3,
                            base_url=config.BASE_URL
                            )
        self.prompt = prompt_loader.load_prompt()
        self.agent = None

    def create_agent(self):
        """
        Create the agent with tools and system prompt.
        """
        try:
            self.agent = create_agent(
                            model = self.llm,
                            tools = [retrieve_context, sql_toolkit],
                            system_prompt= self.prompt
                        )
        except Exception as e:
            print(f"Error while creating agent: {e}")

    def run_query(self, query : str):
        """
        Run a user query and stream the agent's response.
        """
        try:
            for event in self.agent.stream(
                    {"messages": [{"role": "user", "content": query}]},
                    stream_mode="values",
            ):
                event["messages"][-1].pretty_print()

        except Exception as e:
            print(f"Error while querying agent: {e}")

if __name__ == "__main__":
    agent = OrchestratorAgent()
    agent.create_agent()
    agent.run_query("Give me the names of employee with highest salary in each department")