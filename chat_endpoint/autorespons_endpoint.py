import asyncio
import json
import time

from typing import Optional, List

from pydantic import BaseModel, Field

from starlette.responses import StreamingResponse
from fastapi import FastAPI, HTTPException, Request

app = FastAPI(title="OpenAI-compatible API")


# data models
class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: Optional[str] = "gpt-3.5-turbo-0125"
    messages: List[Message]
    stream: Optional[bool] = False
    temperature: float


async def _resp_async_generator(text_resp: str, request: ChatCompletionRequest):
    # let's pretend every word is a token and return it over time
    tokens = text_resp.split(" ")

    for i, token in enumerate(tokens):
        chunk = {
            "id": i,
            "object": "chat.completion.chunk",
            "created": time.time(),
            "model": request.model,
            "choices": [{"delta": {"content": token + " "}}],
        }
        yield f"data: {json.dumps(chunk)}\n\n"
        # await asyncio.sleep(1)
    yield "data: [DONE]\n\n"

@app.get("/", description="Defalt message", response_model=str)
async def default():
    return "This is default page for open ai autorepeat endpoint."

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    if request.messages:
        resp_content = (
            "As a mock AI Assitant, I can only echo your last message: "
            + request.messages[-1].content
        )
    else:
        resp_content = "As a mock AI Assitant, I can only echo your last message, but there wasn't one!"
    if request.stream:
        return StreamingResponse(
            _resp_async_generator(resp_content, request), media_type="application/x-ndjson"
        )

    return {
        "id": "1",
        "object": "chat.completion",
        "created": time.time(),
        "model": request.model,
        "choices": [{"message": Message(role="assistant", content=resp_content)}],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8088)