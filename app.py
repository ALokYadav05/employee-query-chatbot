from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from src import orchest_agent

app = FastAPI()


class UserIn(BaseModel):
    """ Validate user request"""
    query: str = Field(..., description="User query")


@app.post("/user")
def handle_request(req: UserIn):
    """
    Handle user request
    Returns: LLM streaming response
    """
    try:
        def event_stream():
            """ Streams user request """
            for chunk in orchest_agent.run_query(req.query):
                yield chunk

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    except Exception as e:
        def error_stream():
            """" Streams Error """
            yield f"Error: {str(e)}"

        return StreamingResponse(error_stream(), media_type="text/event-stream")
