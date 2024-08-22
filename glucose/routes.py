import polars as pl
import thefuzz.fuzz as fuzz
from fastapi import APIRouter
from polars import DataFrame
import httpx
from fastapi import FastAPI, HTTPException, Header, Request, APIRouter
from pydantic import BaseModel
from typing import Optional


glucose = APIRouter() #FastAPI(title="Anage rest", version="0.1", description="API server to handle queries to restful_anage", debug=True)

class PredictGlucose(BaseModel):
    question: str
    session_id: str = ""
    conversation_history: str = ""
    gpt_version: str = "gpt-4"

# Initialize FastAPI app
gpt_router = APIRouter()
# Define the API endpoint
@gpt_router.post("/predict_glucose", summary="Send a question to the LongevityGPT")
async def longevity_gpt(request: PredictGlucose):
    """Send a question to the LongevityGPT"""
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