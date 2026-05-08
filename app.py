import json
from fastapi import FastAPI, status
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from src import orchest_agent
import logging

app = FastAPI()


class UserIn(BaseModel):
    """
    Data model for user input validation.
    Attributes:
         query (str): The natural language query from the employee.
    """
    query: str = Field(..., min_length=0, description="User query that goes to LLM",
                       title="User-Query", examples=["What is company leave policy?"])


@app.post("/user")
async def handle_request(req: UserIn):
    """
      Endpoint to process employee queries and stream LLM responses.
    Args:
        req (UserIn): The request body containing the user's query.
    Returns:
        StreamingResponse: A chunked stream of JSON objects (NDJSON format).
    """
    if not req.query.strip():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Query cannot be empty"}
        )

    async def event_stream():  # Make this async
        """
        Asynchronous generator that grabs tokens from the
        AI agent and turns them into JSON for the frontend.
        """
        try:
            # Iterating over a generator
            async for token in orchest_agent.run_query(req.query):
                if token:
                    # yield as a JSON string followed by a newline
                    yield f"{json.dumps({'response': token})}\n"

        except Exception as e:
            logging.error(f"Stream Error: {e}", exc_info=True)
            yield f"{json.dumps({'error': 'Internal stream error', 'status': 500})}\n"

    return StreamingResponse(
        event_stream(),
        media_type="application/x-ndjson",
        status_code=status.HTTP_200_OK
    )
