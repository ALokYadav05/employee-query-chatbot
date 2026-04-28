# AI Intelligent Employee Query Chatbot

## Overview
**AIEmployeeChatbot** is a FastAPI-based application that integrates **LangChain**, **Ollama**, 
and custom tools to provide intelligent, context-aware responses to employee-related queries. 

It combines:
- **Retrieval-Augmented Generation (RAG)** for HR and role documents  
- **NL2SQL** for querying structured employee databases  
- A central **OrchestratorAgent** that routes queries to the right tool and synthesizes unified answers  
---
## Project Structure

```
Employee_Intelligent_Chatbot/
├── chromadb/                  # Persistent vectorstore
├── data/                      # HR documents
│   ├── HR_Policies_Handbook.docx
│   └── Role_Documents_Handbook.docx
├── src/
│   ├── agent/                 # OrchestratorAgent and system prompt
│   ├── core/                  # Config and prompt loader
│   ├── corpus_index/          # RAGPipeline for building vectorstore
│   ├── database/              # Database connection wrapper
│   ├── prompts/               # System prompt for the agent
│   └── tools/                 # RAGTool and SQLTool implementations
├── .env                       # Environment variables
├── .gitignore                 # Git ignore rules
├──  app.py                    # FastAPI                 
├── poetry.lock
├── pyproject.toml             # Project dependencies & metadata
└── README.md
```


___

## Features
**OrchestratorAgent**  
  - Combines LLM with RagTool and SQLTool.  
  - Loads system prompt (system_prompt.md).  
  - Handles queries via run_query.

**RagTool**  
  - Uses Chroma vectorstore with OllamaEmbeddings.  
  - Retrieves HR policies and role descriptions.  
  - Exposed as retrieve_context.

**SQLTool**  
  - Uses SQLDatabaseToolkit with ChatOllama.  
  - Converts natural language questions into SQL queries.  
  - Executes queries safely (only SELECT statements).  
  - Exposed as query_tool.

**IndexingPipeline**  
  - Loads HR documents (HR_Policies_Handbook.docx, Role_Documents_Handbook.docx).  
  - Splits into chunks with RecursiveCharacterTextSplitter.  
  - Builds persistent vectorstore (chromadb/).