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
from datetime import datetime

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
    return result

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
    
    # Read the queries from an external file
    query_file = "queries/best_interventions.txt"
    with open(query_file, "r") as f:
        queries = f.readlines()
    
    # Prepare the output file
    output_file = "results/best_interventions_result.txt"
    with open(output_file, "w") as f:
        for query in queries:
            query = query.strip()
            if not query:
                continue
            
            # Run the query
            result= run_query(model, prompt_file, query)
            
            # Prepare the output
            timestamp = datetime.now().isoformat()
            f.write(f"Question: {query}\n")
            f.write(f"Result: {result}\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write("\n---\n\n")  # Add a separator between entries

@app.command()
def test_life_extending_variants():
    model = "gpt-4o-mini"
    prompt_file = "prompts/open_genes.txt"
    query = "Which gene variants are most associated with living longer in multiple populations?"
    run_query(model, prompt_file, query)

if __name__ == "__main__":
    app()
