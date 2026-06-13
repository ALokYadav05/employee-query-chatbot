# AI Intelligent Employee Query Chatbot

**An intelligent conversational AI assistant for employee queries powered by RAG and NL2SQL**

---

## Table of Contents
- [Overview](#-overview)
- [Key Features](#-key-features)
- [Project Architecture & Tools](#-project-architecture--tools)
- [API Endpoints](#-api-endpoints)
- [Quick Start](#-quick-start)
- [Prerequisites](#-prerequisites)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Docker Deployment](#-docker-deployment)

---

## Overview

**AI Intelligent Employee Query Chatbot** is a smart assistant that answers employee-related questions by 
  intelligently combining document-based knowledge with database queries. It uses advanced AI technologies including:

- **LangChain** - For orchestrating AI workflows and tool execution
- **Ollama** - For running local language models
- **ChromaDB** - For storing and retrieving document knowledge
- **FastAPI** - For building the backend REST API
- **Streamlit** - For the user-friendly web interface

Simply ask a question, and the chatbot will find the answer from HR policies, role documents, or employee databases!

---

## Key Features

* **Smart Query Understanding** - Automatically determines if your question needs document lookup or database search.
* **Document Search (RAG)** - Retrieves information from HR policies and role handbooks.
* **Database Query (NL2SQL)** - Converts natural language questions into SQL queries securely.
* **Multi-Chat Session Management** - Create, maintain, and switch between multiple distinct chat sessions seamlessly.
* **Session Control** - Easily rename or delete chat sessions to keep your conversations organized.
* **Real-time Streaming** - Get responses as they're generated, not after processing.
* **Easy Web Interface** - User-friendly Streamlit dashboard featuring a chat history sidebar.
* **Local & Private** - Runs locally using Ollama, no external API calls needed.
* **Containerized** - The application is fully containerized using a Dockerfile and Docker Compose for
   seamless multiservice deployment (FastAPI, MongoDB, MSSQL, and Ollama).

## Project Architecture & Tools

The system uses an **Orchestrator Agent** powered by LangChain to intelligently route user queries to the 
correct tool based on context.

### 1. RAG Retriever Tool
* Used when questions relate to text documents (e.g., HR Policies, company handbooks).
* Queries **ChromaDB** using vector embeddings to find semantic matches and provide contextual answers.

### 2. SQL Tool (NL2SQL Engine)
Used when questions require data from structured tables. The agent relies on **4 specialized LangChain tools** 
to safely and accurately build and execute database queries:


| Tool Name | Input | Description |
| :--- | :--- | :--- |
| **`sql_db_list_tables`** | Empty string (`""`) | Returns a comma-separated list of all tables present in the<br/> database. |
| **`sql_db_schema`** | Comma-separated tables | Returns the precise schema definition and sample rows for the specified tables. |
| **`sql_db_query_checker`** | SQL query string | Validates syntax and structure to prevent errors **before** code execution. |
| **`sql_db_query`** | Verified SQL query string | Executes the query and returns raw data. Handles fallback logic if columns are missing. |

---

## API Endpoints

The FastAPI backend exposes the following endpoints to handle both streaming chat generation and multi-session 
CRUD management:

### Chat Execution
* `POST /chat/{session_id}` - Send a message to a specific chat session and receive a streaming response.

### Session Management
* `POST /sessions` - Create a new chat session (Returns `CreateSessionResponse`, Status: `201 Created`).
* `GET /sessions` - Fetch all active chat sessions for the sidebar.
* `GET /sessions/{session_id}` - Retrieve a single chat session's structural details.
* `PATCH /sessions/{session_id}` - Rename or update an existing chat session's title (Status: `200 OK`).
* `DELETE /sessions/{session_id}` - Permanently wipe a chat session and its history.

---

## Quick Start

Run the full AI Employee Query Chatbot using Docker Compose.


### 1. Clone the Repository

```bash
git clone https://github.com/ALokYadav05/Employee_Intelligent_Chatbot.git
cd Employee_Intelligent_Chatbot
```

### 2. Build Application Image

```bash
docker build -t ai-employee-chatbot .
```

### 3. Pull Required Service Images

```bash
docker pull mongo:latest
docker pull mcr.microsoft.com/mssql/server:2025-latest
docker pull ollama/ollama:latest
```

### 4. Start All Services

```bash
docker compose up -d
```

This will start:

- Application (FastAPI + Streamlit)
- MongoDB
- MSSQL Server
- Ollama

### 5. Verify Containers

```bash
docker ps
```

## First-Time Initialization (Required Once)

### 6. Create MSSQL Database

```bash
docker exec -it mssql bash
```

```bash
/opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P <password> -C
```

```sql
CREATE DATABASE employeeDBMaster;
GO
```

### 7. Pull Ollama Models

```bash
docker exec -it ollama bash
```

```bash
ollama pull mxbai-embed-large
ollama pull sqlcoder:15b
ollama pull mistral-nemo
ollama pull qwen3:4b
```

### 8. Build ChromaDB Index

```bash
docker exec -it employee-chatbot bash
```

```bash
python -m src.corpus_index.indexing
```

### 9. Restart Application Container

```bash
docker restart employee-chatbot
```

### 10. Access Application

- FastAPI → http://localhost:8000  
- Streamlit → http://localhost:8501

Open `http://localhost:8501` in your browser and start asking questions! 

---

## Prerequisites

Before you begin, make sure you have these installed:


| Software | Version | Purpose |
|----------|---------|---------|
| **Python** | 3.13+ | Required for the application |
| **Poetry** | 2.0+ | Dependency management tool |
| **Ollama** | Latest | Runs the AI language model locally |
| **Git** | Any | To clone the repository |

---

##  Project Structure

```
Employee_Intelligent_Chatbot/
│
├──  app.py                    # Main API server (FastAPI)
├──  pyproject.toml            # Project configuration & dependencies
├──  poetry.lock               # Locked dependency versions
├──  .env                      # Environment configuration
├──  requirements.txt          # all dependency
├──  Dockerfile                # docker file for application image 
├──  docker-compose.yml        # multi-container setup
│
├── frontend/
│   └── app.py                   # Web interface (Streamlit)
│
├── data/                     # Documents (the knowledge base)
│   ├── HR_Policies_Handbook.docx
│   └── Role_Documents_Handbook.docx
│
├── chromadb/                 # Vector database (auto-created)
│   └── [indexed documents]
│
└── src/                      # Core application code
    ├── agent/
    │   └── orchestrator.py      # Brain: routes queries to right tool
    ├── core/
    │   ├── config.py            # Configuration loader
    │   └── prompt_loader.py     # System prompts
    ├── corpus_index/
    │   └── indexing.py          # Document indexing pipeline
    ├── database/
    │   ├── mongo_connector.py   # MongoDB connection
    │   └── sql_connector.py     # SQL database connection
    ├── prompts/
    │   └── system_prompt.md     # AI system instructions
    └── tools/
        ├── rag_retriever_tool.py  # Document search tool
        └── sql_tool.py            # Database query tool
```

---

##  How It Works

### The Query Flow

```
                  User Question
                       ↓
    ┌─────────────────────────────────────────┐
    │   OrchestratorAgent (The Brain)         │
    │   "Should I search documents or DB?"    │
    └──────────┬──────────────────────┬───────┘
               ↓                      ↓
     ┌────────────────┐    ┌──────────────────┐
     │  RAG Tool      │    │   SQL Tool       │
     │ (Search Docs)  │    │ (Query Database) │
     └────────────────┘    └──────────────────┘
             ↓                      ↓
      ┌────────────────────────────────────┐
      │  Combine Answers & Return Response │
      └────────────────────────────────────┘
                      ↓
                 User Response
```
