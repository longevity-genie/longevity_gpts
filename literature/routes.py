# TODO with ideas from https://fastapi.tiangolo.com/tutorial/bigger-applications/ import routes of submodules
import os
import re
from pathlib import Path

import loguru
import torch
from dotenv import load_dotenv
from fastapi import APIRouter
from functional import seq
from hybrid_search.opensearch_hybrid_search import *
from langchain_community.embeddings.huggingface import HuggingFaceBgeEmbeddings, HuggingFaceEmbeddings
from pycomfort.config import load_environment_keys
from literature.models import QueryPaper


def init_embeddings(model_name: str = "bge-base-en-v1.5", device: Optional[str] = None, normalize_embeddings: bool = True):
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    model_kwargs = {'device': device}
    encode_kwargs = {'normalize_embeddings': normalize_embeddings} # set True to compute cosine similarity
    return HuggingFaceBgeEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs) if "bge" in model_name else HuggingFaceEmbeddings(model_name=model_name,
                                                                                  model_kwargs=model_kwargs,
                                                                                  encode_kwargs=encode_kwargs)

literature_router = APIRouter()


def resolve_environment():
    current_file_dir = Path(__file__).parent
    env_here = current_file_dir / ".env"
    e = env_here if env_here.exists() else current_file_dir / ".env"
    load_dotenv(e, verbose=True, override=True)
    return e


env_path = resolve_environment()
default_embedding = os.getenv("DEFAULT_EMBEDDING", "BAAI/bge-large-en-v1.5")

def get_collection_exceptions():
    path = Path(Path(__file__).parent, "collections_exceptions.txt")
    exceptions = dict()
    with open(path) as f:
        lines = f.readlines()
        for line in lines:
            collection, model = line.split(" ")
            exceptions[collection] = model
    return exceptions

collections_models_map = get_collection_exceptions()

def extract_from_collection(collection: str, default: str = "BAAI/bge-large-en-v1.5") -> Optional[str]:
    """
    Extracts a portion of a string based on specific patterns.
    First, it looks for 'paragraph_number_' or 'papers_number_'.
    If found, it extracts everything after the number and '_'.
    If not found, it extracts everything after 'paragraphs' or 'papers'.

    :param collection: The string to be processed.
    :return: The extracted string portion, or None if no relevant pattern is found.
    """
    # Try to extract after "paragraph_number_"
    paragraph_num_match = re.search(r"paragraph_(\d+)_", collection)
    if paragraph_num_match:
        # Extract everything after the number and "_"
        start_index = paragraph_num_match.end()
        return collection[start_index:].replace("_", "-")

    # Try to extract after "papers_number_"
    papers_num_match = re.search(r"papers_(\d+)_", collection)
    if papers_num_match:
        # Extract everything after the number and "_"
        start_index = papers_num_match.end()
        return collection[start_index:].replace("_", "-")

    # If no number patterns found, try to extract after "paragraphs" or "papers"
    paragraph_match = re.search(r"paragraphs_", collection)
    if paragraph_match:
        start_index = paragraph_match.end()
        return collection[start_index:].replace("_", "-")

    papers_match = re.search(r"papers_", collection)
    if papers_match:
        start_index = papers_match.end()
        return collection[start_index:].replace("_", "-")

    # Return default if no pattern matched
    return default
# "aging_papers_paragraphs_bge_base_en_v1.5", "aging_papers_paragraphs_specter2", "papers_5_bge-large"
def resolve_embeddings(collection_name: str):
    model_name = collections_models_map.get(collection_name)
    if model_name:
        return init_embeddings(model_name)

    model_name = extract_from_collection(collection_name, default_embedding)
    if "bge" in model_name and "BAAI" not in model_name:
        model_name = f"BAAI/{model_name}"
    elif "specter" in model_name and "allenai" not in model_name:
        model_name = f"allenai/specter2_base"
    print(f"MODEL NAME IS {model_name}")
    return init_embeddings(model_name)


def search_collection(collection_name: str, text: str, k: int, url: str) -> list[(Document, float)]:
    """
    Searches specific collection
    :param collection_name:
    :param text:
    :param k: limit the text
    :param url:
    :return:
    """
    embeddings = resolve_embeddings(collection_name)
    timeout = 60
    docsearch = OpenSearchHybridSearch.create(url, collection_name, embeddings, request_timeout=timeout) #TODO call resolve embeddings
    # results: list[(Document, float)] = docsearch.similarity_search_with_score(text, k=k, search_type = HYBRID_SEARCH, search_pipeline = "norm-pipeline", timeout=timeout)
    results: list[(Document, float)] = docsearch.hybrid_search(text, k=k, search_pipeline = "norm-pipeline", timeout=timeout)
    for r in results:
        r[0].metadata["search_score"] = r[1]
        r[0].metadata["collection_name"] = collection_name
    return [r[0] for r in results]


@literature_router.post("/hybrid_search/", description="does hybrid search in the literature, provides sources together with answers", response_model=List[str])
async def hybrid_search(query: QueryPaper):
    collections: list[str] = query.collections
    text = query.text
    k = query.limit
    url = query.db if query.db is not None else os.getenv("OPENSEARCH_URL", "https://localhost:9200")
    loguru.logger.info(f"HYBRID SEARCH ON: '{query.text}' \n in collections {query.collections} with limit = {k} and url = {url}")
    results = seq([search_collection(collection_name, text, k, url) for collection_name in collections]).flatten().order_by(lambda d: d.metadata["search_score"]).reverse()
    loguru.logger.info(f"RESULTS RECEIVED:\n {results}")
    def document_to_string(d: Document)-> str:
        source = 'http://doi.org/'+d.metadata['doi'] if 'doi' in d.metadata and d.metadata['doi'] is not None else d.metadata['source']
        score = d.metadata["search_score"]
        collection_name = d.metadata["collection_name"]
        result:str = f"""
        {d.page_content}
        SOURCE: {source}"""
        if not query.verbose:
            return result
        else:
            return f"""{result}
                SEARCH_SCORE: {score}
                COLLECTION_NAME: {collection_name}
                """
    return [document_to_string(d) for d in results]