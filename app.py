from fastapi import FastAPI
from pydantic import BaseModel
from src import agent

app = FastAPI()


class UserRequest(BaseModel):
    """ Validate user request"""
    query: str


class AIResponse(BaseModel):
    """ Validate AI response """
    response: str
    status: str


@app.post("/user")
def handle_request(req: UserRequest):
    """
    Handle user request
    Returns: AI response
    """
    try:
        response = agent.run_query(req.query)
        if str(response) is None:
            print("data not found")
        return AIResponse(
            response=str(response),
            status="200"
        )

    except Exception as e:
        return AIResponse(
            response=str(e),
            status="442"
        )
