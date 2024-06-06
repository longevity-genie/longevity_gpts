import time
from pathlib import Path
from fastapi import FastAPI
from just_agents.llm_session import LLMSession
from literature.routes import hybrid_search
from gpt.routes import longevity_gpt
from genetics.main import rsid_lookup, gene_lookup, pathway_lookup, disease_lookup, sequencing_info
from dotenv import load_dotenv
load_dotenv(override=True)
# What is the influence of different alleles in  rs10937739?
app = FastAPI(title="Genetics Genie API endpoint.")


@app.get("/", description="Defalt message", response_model=str)
async def default():
    return "This is default page for Genetics Genie API endpoint."


@app.post("/v1/chat/completions")
async def chat_completions(request: dict):
    print(request)
    curent_llm = {
        "model":request["model"],
        "temperature":request["temperature"]
    }
    session: LLMSession = LLMSession(
        llm_options=curent_llm,
        tools=[hybrid_search, longevity_gpt, rsid_lookup, gene_lookup, pathway_lookup, disease_lookup, sequencing_info]
    )
    with open(Path(Path(__file__).parent, "data", "system_prompt.txt")) as sys_prompt:
        session.instruct(sys_prompt.read())

    if request["messages"]:
        session.memory.add_messages(request["messages"], False)
        resp_content = session.query()
    else:
        resp_content = "Something goes wrong, request did not contain messages!!!"

    return {
        "id": "1",
        "object": "chat.completion",
        "created": time.time(),
        "model": curent_llm["model"],
        "choices": [{"message": {"role":"assistant", "content":resp_content}}],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8088)