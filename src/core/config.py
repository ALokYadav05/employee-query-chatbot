import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    def __init__(self):
        self.BASE_DIR = Path(__file__).parent.parent.parent    #base directory
        self.HR_POLICIES_PATH = os.getenv("HR_POLICIES_PATH")   # rag-doc
        self.ROLE_DOCS_PATH = os.getenv("ROLE_DOCS_PATH")        # rag-doc
        self.EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL")
        self.BASE_URL = os.getenv("BASE_URL")
        self.MISTRAL_NEMO = os.getenv("MISTRAL_NEMO")
        self.SQL_CONN_URL = os.getenv("SQL_CONN_URL")
        self.OLLAMA_NLP2SQL = os.getenv("OLLAMA_NLP2SQL")
        self.GEMMA_CLOUD_MODEL = os.getenv("GEMMA_CLOUD_MODEL")

config = Config()
