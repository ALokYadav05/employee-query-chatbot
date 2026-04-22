import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.HR_POLICIES_PATH = os.getenv("HR_POLICIES_PATH")
        self.ROLE_DOCS_PATH = os.getenv("ROLE_DOCS_PATH")
        self.EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL")
        self.BASE_URL = os.getenv("BASE_URL")

config = Config()
