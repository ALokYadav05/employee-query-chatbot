from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
from src.core.config import config


class IndexingPipeline:
    """ RAG-Pipeline for Indexing documents"""

    def __init__(self):
        self.BASE_DIR = config.BASE_DIR
        self.EMBEDDING_MODEL = config.EMBEDDING_MODEL
        self.files = [f"{self.BASE_DIR}/data/HR_Policies_Handbook.docx",
                      f"{self.BASE_DIR}/data/Role_Documents_Handbook.docx"]

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=200
        )

        self.all_chunks = []

        self.embedding = OllamaEmbeddings(
            base_url=config.BASE_URL,
            model=self.EMBEDDING_MODEL
        )

    def doc_loader(self):
        """
        Load file paths specified in self.files
        returns: A list of langchain documents objects
        """
        docs = []
        try:
            for file in self.files:
                loader = UnstructuredLoader(file)
                docs.extend(loader.load())
            print("Document's are Loaded Successfully!")
            return docs

        except FileNotFoundError as e:
            print(f"File not found: {e}")
        except Exception as e:
            print(f"Error occurred while loading {e}")

    def text_splitter(self, docs):
        """
        Split loaded documents into smaller chunks for embedding.
        Args: list of documents returned by doc_loader
        """
        try:
            splitter = self.splitter
            split_text = splitter.split_documents(docs)
            self.all_chunks.extend(split_text)
            print("Chunks formed successfully!")

        except Exception as e:
            print(f"Error occurred while splitting {e}")

    def create_vector_store(self):
        """
        Generate embeddings for all chunks and store them in ChromaDB.
        returns: ChromaDB that stores embeddings
        """
        try:
            store = Chroma.from_documents(
                documents=self.all_chunks,
                embedding=self.embedding,
                persist_directory=f"{self.BASE_DIR}/chromaDB",  # store Chromadb folder in root
            )
            print("Stored embeddings successfully!")
            return store
        except Exception as e:
            print(f"Error occurred while creating Vector-store: {e}")

    def run_pipeline(self):
        """
        load → split → embed → store
        Returns: Chroma vector store
        """
        try:
            docs = self.doc_loader()
            self.text_splitter(docs)
            return self.create_vector_store()
        except Exception as e:
            print(f"Error occurred while running pipeline : {e}")


rag_index = IndexingPipeline()
rag_index.run_pipeline()
