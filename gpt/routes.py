import httpx
from fastapi import FastAPI, HTTPException, Header, Request, APIRouter
from pydantic import BaseModel
from typing import Optional

# Define Pydantic models
class AnswerRequest(BaseModel):
    question: str
    session_id: str = ""
    conversation_history: str = ""
    gpt_version: str = "gpt-4"

class AnswerResponse(BaseModel):
    answer: str
    references: Optional[str] = None

# Initialize FastAPI app
gpt_router = APIRouter()
# Define the API endpoint
@gpt_router.post("/longevity_gpt", response_model=AnswerResponse, summary="Send a question to the LongevityGPT")
async def longevity_gpt(request: AnswerRequest):
    # Forwarding the request to the external API
    async with httpx.AsyncClient(timeout=90) as client:
        response = await client.post(
            "https://www.asklongevitygpt.com/answer",
            json=request.dict(),
            headers={"Content-Type": "application/json"}
        )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error from LongevityGPT API")

        return response.json()