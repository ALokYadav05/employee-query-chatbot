import json
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from src import orchest_agent

app = FastAPI()


class UserIn(BaseModel):
    """
    Data model for user input validation.
    Attributes:
         query (str): The natural language query from the employee.
    """
    query: str = Field(..., description="User query")


@app.post("/user")
async def handle_request(req: UserIn):
    """
      Endpoint to process employee queries and stream LLM responses.
    Args:
        req (UserIn): The request body containing the user's query.
    Returns:
        StreamingResponse: A chunked stream of JSON objects (NDJSON format).
    """

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
                    yield f"{json.dumps({
                        'response': token
                    })}\n"

        except Exception as e:
            yield f"{json.dumps({
                'error': str(e)
            })}\n"

    return StreamingResponse(
        event_stream(),
        media_type="application/x-ndjson"
    )
