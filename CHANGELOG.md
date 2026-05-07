# Changelog

All the notable changes to this project will be documented in this file.

---

## [0.1.0] - 2026-05-07

### Added
- **Core Orchestration**: Introduced `OrchestratorAgent` to route queries between RAG and SQL tools.
- **LLM Integration**: Full integration with Ollama for natural language processing and embeddings.
- **Streaming**: Real-time response support via the new `/user` endpoint.
- **Tools**: 
    - RAG Tool for document retrieval using ChromaDB and LangChain.
    - SQL Tool for natural language to SQL conversion.
- **Storage**: Multi-database support with SQLite, MongoDB, and ChromaDB vector store.
- **API**: FastAPI backend with Pydantic validation and RESTful endpoints.
- **Project Foundation**: Modular structure, Poetry dependency management, and comprehensive documentation.


