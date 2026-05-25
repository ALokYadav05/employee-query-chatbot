import json
import uuid
import logging
from typing import Optional
from fastapi import FastAPI, status, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from src import OrchestratorAgent
from src.database import MongoDBConn  # <-- use your wrapper

app = FastAPI()
orchest_agent = OrchestratorAgent()

# Initialize MongoDB connection
mongo_conn = MongoDBConn()
db_client = mongo_conn.client
db = mongo_conn.db
sessions_collection = db["sessions"]


class UserIn(BaseModel):
    query: str = Field(..., min_length=1, description="User query that goes to LLM",
                       title="User-Query", examples=["What is company leave policy?"])


class CreateSessionRequest(BaseModel):
    title: Optional[str] = None


class CreateSessionResponse(BaseModel):
    id: str
    title: str


class MessageModel(BaseModel):
    role: str
    content: str


class UpdateSessionRequest(BaseModel):
    title: str


@app.post("/chat/{session_id}")
async def handle_request(session_id: str, req: UserIn):
    """
    Endpoint to process employee queries and stream LLM responses.
    Args:
        req (UserIn): The request body containing the user's query.
        session_id : session ID
    Returns:
        StreamingResponse: A chunked stream of JSON objects (NDJSON format).
    """
    if not req.query.strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Query cannot be empty"}
        )

    # First verify if the session even exists before starting the stream
    session = sessions_collection.find_one({"_id": session_id})
    if not session:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "Session not found"}
        )

    async def event_stream():
        """
        Asynchronous generator that grabs tokens from the
        AI agent and turns them into JSON for the frontend.
        """
        try:
            collected_response = ""
            async for token in orchest_agent.run_query(req.query):
                if token:
                    collected_response += token
                    yield f"{json.dumps({'response': token})}\n"

            # Use $each to insert separate flat objects instead of a nested array
            sessions_collection.update_one(
                {"_id": session_id},
                {
                    "$push": {
                        "messages": {
                            "$each": [
                                {"role": "user", "content": req.query},
                                {"role": "assistant", "content": collected_response}
                            ]
                        }
                    }
                }
            )

        except Exception as e:
            logging.error(f"Stream Error: {e}", exc_info=True)
            yield f"{json.dumps({'error': 'Internal stream error', 'status': 500})}\n"

    return StreamingResponse(
        event_stream(),
        media_type="application/x-ndjson",
        status_code=status.HTTP_200_OK
    )


@app.post("/sessions", response_model=CreateSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(payload: CreateSessionRequest):
    """
    Create a new chat session with a unique ID and title.
    """
    session_id = str(uuid.uuid4())
    title = payload.title or "New Chat"

    session_document = {
        "_id": session_id,
        "title": title,
        "messages": []
    }
    sessions_collection.insert_one(session_document)
    return {"id": session_id, "title": title}


@app.get("/sessions")
def list_sessions():
    """
    Retrieve a list of all existing chat sessions.
    """
    sessions = sessions_collection.find()
    return [
        {
            "id": doc["_id"],
            "title": doc.get("title", "New Chat"),
            "messages": doc.get("messages", [])
        }
        for doc in sessions
    ]


@app.get("/sessions/{session_id}")
def get_session(session_id: str):
    """
    Get the full details and message history of a specific session.
    """
    session = sessions_collection.find_one({"_id": session_id})
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return {
        "id": session["_id"],
        "title": session.get("title", "New Chat"),
        "messages": session.get("messages", [])
    }


@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    """
    Permanently delete a specific chat session by its ID.
    """
    result = sessions_collection.delete_one({"_id": session_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return {"status": "deleted", "id": session_id}


@app.post("/sessions/{session_id}/messages", status_code=status.HTTP_201_CREATED)
def append_message(session_id: str, message: MessageModel):
    """
    Manually append a single message to a session's history.
    """
    new_message = {"role": message.role, "content": message.content}
    result = sessions_collection.update_one(
        {"_id": session_id},
        {"$push": {"messages": new_message}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return {"status": "ok"}


@app.patch("/sessions/{session_id}", status_code=status.HTTP_200_OK)
def update_session(session_id: str, payload: UpdateSessionRequest):
    """
    Update the title of an existing chat session.
    """
    result = sessions_collection.update_one(
        {"_id": session_id},
        {"$set": {"title": payload.title}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    return {"status": "updated", "id": session_id, "title": payload.title}
