import typer
from open_genes.tools import db_query
import asyncio
import json
import pprint
import os
from dotenv import load_dotenv
from just_agents.llm_session import LLMSession
from just_agents.utils import rotate_env_keys
from pathlib import Path

app = typer.Typer()

def run_query(model: str, prompt_file: str, query: str):
    load_dotenv(override=True)

    llm_options = {
        "model": model,
        "temperature": 0.0
    }

    system_prompt_path = Path(prompt_file)

    with system_prompt_path.open("r") as f:
        system_prompt = f.read().strip()

    session: LLMSession = LLMSession(
        llm_options=llm_options,
        tools=[db_query]
    )
    session.memory.add_system_message(system_prompt)
    session.memory.add_on_message(lambda m: pprint.pprint(m) if "content" in m is not None else None)

    result = session.query(query)
    typer.echo("RESULT:================================")
    typer.echo(result)

@app.command()
def custom_query(
    model: str = typer.Option("gpt-4o-mini", help="Name of the model to use"),
    prompt_file: str = typer.Option("prompts/open_genes.txt", help="Path to the system prompt file"),
    query: str = typer.Option(..., help="Query to run")
):
    run_query(model, prompt_file, query)

@app.command()
def test_best_interventions():
    model = "gpt-4o-mini"
    prompt_file = "prompts/open_genes.txt"
    query = "Give me which genes extended lifespan most of all on model organisms"
    run_query(model, prompt_file, query)

if __name__ == "__main__":
    app()
