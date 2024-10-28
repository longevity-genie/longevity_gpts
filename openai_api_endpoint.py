import time
from pathlib import Path
from fastapi import FastAPI, Request
from just_agents.interfaces.IAgent import build_agent, IAgent
from just_agents.llm_session import LLMSession
from literature.routes import _hybrid_search
from genetics.main import rsid_lookup, gene_lookup, pathway_lookup, disease_lookup, sequencing_info
from clinical_trials.clinical_trails_router import _process_sql, clinical_trails_full_trial
from precious3GPT.p3gpt_tool import get_omics_data, get_enrichment
from precious3GPT.routes import omics_router
from starlette.responses import StreamingResponse
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from open_genes.tools import db_query
import loguru
import yaml

log_path = Path(__file__)
log_path = Path(log_path.parent, "logs", "openai_api_endpoint.log")
loguru.logger.add(log_path.absolute(), rotation="10 MB")


load_dotenv(override=True)
# What is the influence of different alleles in rs10937739 and what is MTOR gene?
app = FastAPI(title="Genetics Genie API endpoint.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(omics_router)

TOOLS = [_hybrid_search, rsid_lookup, gene_lookup, pathway_lookup, disease_lookup, sequencing_info,
             _process_sql, clinical_trails_full_trial, db_query, get_omics_data, get_enrichment, _hybrid_search]

@app.get("/", description="Defalt message", response_model=str)
def default():
    return "This is default page for Genetics Genie API endpoint."


def clean_messages(request: dict):
    for message in request["messages"]:
        if message["role"] == "user":
            content = message["content"]
            if type(content) is list:
                if len(content) > 0:
                    if type(content[0]) is dict:
                        if content[0].get("type", "") == "text":
                            if type(content[0].get("text", None)) is str:
                                message["content"] = content[0]["text"]


def remove_system_prompt(request: dict):
    if request["messages"][0]["role"] == "system":
        request["messages"] = request["messages"][1:]


def get_agent(request):
    with open("endpoint_options.yaml") as f:
        agent_schema = yaml.full_load(f).get(request["model"])

    return build_agent(agent_schema)


@app.post("/v1/chat/completions")
def chat_completions(request: dict):
    try:
        loguru.logger.debug(request)
        # options = get_options(request)
        # session = get_session(options)
        agent:IAgent = get_agent(request)
        clean_messages(request)
        remove_system_prompt(request)
        if request["messages"]:
            if request.get("stream") and str(request.get("stream")).lower() != "false":
                return StreamingResponse(
                    agent.stream(request["messages"]), media_type="application/x-ndjson"
                )
            resp_content = agent.query(request["messages"])
        else:
            resp_content = "Something goes wrong, request did not contain messages!!!"
    except Exception as e:
        loguru.logger.error(str(e))
        resp_content = str(e)
    return {
        "id": "1",
        "object": "chat.completion",
        "created": time.time(),
        "model": request["model"],
        "choices": [{"message": {"role": "assistant", "content": resp_content}}],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("openai_api_endpoint:app", host="0.0.0.0", port=8088)

