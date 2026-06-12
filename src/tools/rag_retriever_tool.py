from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from src.core import Config
from langchain.tools import tool
import logging

config = Config()


class RagTool:
    def __init__(self):
        try:
            self.base_dir = config.BASE_DIR
            self.embeddings_model = config.EMBEDDING_MODEL

            # Initialize embedding model
            self.embedding = OllamaEmbeddings(
                base_url=config.BASE_URL,
                model=self.embeddings_model
            )

            # Initialize vector store
            self.vector_store = Chroma(
                embedding_function=self.embedding,
                persist_directory="/app/chromaDB",
            )

            logging.info("RAGTool initialized successfully with Chroma vector store.")
        except Exception as e:
            logging.error(f"Error initializing RAGTool: {e}", exc_info=True)

    def create_retriever(self):
        """
        load vector store
        Returns: chromaDB vector-store object
        """
        try:
            retriever = self.vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={
                    "k": 3,
                    "fetch_k": 12,
                    "lambda_mult": 0.75
                }
            )
            logging.info("Retriever created successfully.")
            return retriever
        except Exception as e:
            logging.error(f"Error creating retriever: {e}", exc_info=True)

    def rag_query_tool(self):
        """
        Expose a LangChain tool for retrieving context from HR policies and role documents.
        """
        retriever = self.create_retriever()

        @tool(
            "rag_retriever",
            description="Retrieve information from HR policies and role documents using embeddings stored in ChromaDB."
        )
        def run_rag_query(query: str):
            """
            Run MMR search on vector store and return retrieved content.
            """
            try:
                response = retriever.invoke(query)
                result = "\n\n".join(
                    f"Content: {doc.page_content}" for doc in response
                )
                logging.info(f"RAG query executed successfully for input: {query}")
                return result
            except Exception as e:
                logging.error(f"Error while retrieving context: {e}", exc_info=True)
                return {"error": f"Failed to retrieve context: {str(e)}"}

        return run_rag_query
