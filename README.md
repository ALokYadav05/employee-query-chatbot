# AI Intelligent Employee Query Chatbot

**An intelligent conversational AI assistant for employee queries powered by RAG and NLP2SQL**


---

##  Table of Contents
- [Overview](#-overview)
- [Key Features](#-key-features)
- [Quick Start](#-quick-start)
- [Prerequisites](#-prerequisites)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)


---

##  Overview

**AI Intelligent Employee Query Chatbot** is a smart assistant that answers employee-related questions by intelligently combining document-based knowledge with database queries. It uses advanced AI technologies including:

- **LangChain** - For orchestrating AI workflows
- **Ollama** - For running local language models
- **ChromaDB** - For storing and retrieving document knowledge
- **FastAPI** - For building the web API
- **Streamlit** - For the user-friendly web interface

Simply ask a question, and the chatbot will find the answer from HR policies, role documents, or employee databases!

---

##  Key Features

 **Smart Query Understanding** - Automatically determines if your question needs document lookup or database search  
 **Document Search (RAG)** - Retrieves information from HR policies and role handbooks  
 **Database Query (NL2SQL)** - Converts natural language questions into SQL queries  
 **Real-time Streaming** - Get responses as they're generated, not after processing  
 **Easy Web Interface** - User-friendly Streamlit dashboard  
 **Local & Private** - Runs locally using Ollama, no external API calls needed  

---

##  Quick Start

Get the chatbot running in 5 minutes:

```bash
# 1. Clone the repository
git clone https://github.com/ALokYadav05/Employee_Intelligent_Chatbot.git
cd Employee_Intelligent_Chatbot

# 2. Install dependencies
poetry install

# 3. Start Ollama (in a new terminal)
ollama serve

# 4. In another terminal, start the API
poetry shell
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# 5. In a third terminal, start the web interface
streamlit run frontend/app.py
```

Open `http://localhost:8501` in your browser and start asking questions! 

---

##  Prerequisites

Before you begin, make sure you have these installed:

| Software | Version | Purpose |
|----------|---------|---------|
| **Python** | 3.13+ | Required for the application |
| **Poetry** | 2.0+ | Dependency management tool |
| **Ollama** | Latest | Runs the AI language model locally |
| **Git** | Any | To clone the repository |

##  Project Structure

```
Employee_Intelligent_Chatbot/
│
├──  app.py                    # Main API server (FastAPI)
├──  pyproject.toml            # Project configuration & dependencies
├──  poetry.lock               # Locked dependency versions
├──  .env                      # Environment configuration
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
