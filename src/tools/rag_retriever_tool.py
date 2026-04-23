from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from src.core import config
from langchain.tools import tool

def load_vector_store ():
    """
    load vector store
    Returns: chromaDB vector-store object
    """
    try:
        base_dir = config.BASE_DIR
        embeddings_model = config.EMBEDDING_MODEL
        embedding = OllamaEmbeddings(
                            base_url=config.BASE_URL,
                            model=embeddings_model
                        )
        chroma_vector_store = Chroma(
                                embedding_function=embedding,
                                persist_directory=f"{base_dir}/chromaDB",
                            )
        return chroma_vector_store
    except Exception as e:
        print(f"Error While initializing vector store: {e}")


@tool("rag_retriever",
      description="Retrieve information from HR policies and role documents."
                  "Using embedding stored in chromaDB",
      )
def retrieve_context(query: str):
    """
    Run MMR search on vector store.
    Returns: result retrieved content
    """
    try:
        vector_store = load_vector_store ()
        retrieved_content = vector_store.as_retriever(
                                            search_type='mmr',
                                            search_kwargs= {
                                                'k' : 3,
                                                'fetch_k' : 12,
                                                'lambda_mult' : 0.75
                                            }
                                        )
        response = retrieved_content.invoke(query)
        result = "\n\n".join(
                        f"Content: {doc.page_content}"
                        for doc in response
                      )
        return result
    except Exception as e:
        print(f"Error While retrieving context: {e}")