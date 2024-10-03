import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import typer
from open_genes.tools import db_query
import asyncio
import json
import pprint

from dotenv import load_dotenv
from just_agents.llm_session import LLMSession
from just_agents.utils import rotate_env_keys
from pathlib import Path
from datetime import datetime
from eliot import start_action, to_file, log_call, log_message
from eliottree import tasks_from_iterable, render_tasks




app = typer.Typer()

logs = Path("logs")
logs.mkdir(parents=True, exist_ok=True)

# Determine the log file mode
log_file_path = logs /  "test_opengenes.log"  # Correct path
log_file_mode = 'w'

try:
    to_file(log_file_path.open(log_file_mode, encoding="utf-8"))
except FileNotFoundError as e:
    print(f"Error: {e}")
    # Handle the error or exit
    exit(1)

@log_call()
def run_query(model: str, prompt_file: str, query: str):
    load_dotenv(override=True)

    llm_options = {
        "model": model,
        "temperature": 0.0
    }

    system_prompt_path = Path(prompt_file)

    with system_prompt_path.open("r", encoding="utf-8") as f:
        system_prompt = f.read().strip()

    session: LLMSession = LLMSession(
        llm_options=llm_options,
        tools=[db_query]
    )
    session.memory.add_system_message(system_prompt)
    session.memory.add_on_message(lambda m: pprint.pprint(m) if "content" in m is not None else None)

    with start_action(action_type="run_query", query=query):
        log_message("prompt_sent_to_llm")
        log_message({"prompt": system_prompt})
        result = session.query(query)
        
        log_message("sql_query_sent_to_db")
        log_message({"query": query})

        log_message("result_handled_through_llm_reply")
        log_message({"result": result})
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
def test_opengenes():
    model = "gpt-4o-mini"
    prompt_file = Path("prompts/open_genes.txt")
    
    # Read the queries from an external file
    query_file = Path("queries/test_opengenes.txt")
    with query_file.open("r", encoding="utf-8") as f:
        queries = f.readlines()
    
    for query in queries:
        query = query.strip()
        if not query:
            continue
        result = run_query(model, str(prompt_file), query)
    
    
    # Render the log to a human-readable file
    human_log_file_path = log_file_path.with_stem(log_file_path.stem + "_human")
    with human_log_file_path.open("w", encoding="utf-8") as human_log_file:
        if log_file_path.exists():
            with log_file_path.open("r", encoding="utf-8") as log_file:
                log_entries = [json.loads(line) for line in log_file]
                tasks = tasks_from_iterable(log_entries)
                render_tasks(human_log_file.write, tasks, human_readable=True)
        else:
            typer.echo("Log file does not exist.")

@app.command()
def render_log():
    """
    Render the Eliot log file in a human-readable tree format.
    """
    if os.path.exists(log_file_path):
        with open(log_file_path, "r", encoding="utf-8") as log_file:
            log_entries = [json.loads(line) for line in log_file]
            tasks = tasks_from_iterable(log_entries)
            render_tasks(sys.stdout.write, tasks, colorize=True, human_readable=True)
    else:
        typer.echo("Log file does not exist.")

@app.command()
def test_life_extending_variants():
    model = "gpt-4o-mini"
    prompt_file = "prompts/open_genes.txt"
    query = "Which gene variants are most associated with living longer in multiple populations?"
    run_query(model, prompt_file, query)

if __name__ == "__main__":
    app()
