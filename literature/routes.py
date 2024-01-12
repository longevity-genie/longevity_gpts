# TODO with ideas from https://fastapi.tiangolo.com/tutorial/bigger-applications/ import routes of submodules
from fastapi import APIRouter
from hybrid_search.opensearch_hybrid_search import *

from literature.models import *


literature_router = APIRouter()


@literature_router.post("/hybrid_search/", description="does hybrid search in the literature, provides sources together with answers", response_model=List[str])
async def hybrid_search(query: QueryPaper):
    loguru.logger.info(f"HYBRID SEARCH ON: '{query.text}'")

    collection_name = query.collection_name
    text = query.text
    k = query.limit
    url = query.db if query.db is not None else os.getenv("OPENSEARCH_URL", "http://localhost:9200")
    docsearch = OpenSearchHybridSearch.create(url, collection_name, embeddings) #TODO call resolve embeddings
    results: list[Document] = docsearch.similarity_search(text, k=k, search_type = HYBRID_SEARCH, search_pipeline = "norm-pipeline")
    loguru.logger.info(f"RESULTS RECEIVED:\n {results}")
    def document_to_string(d: Document)-> str:
        return f"{d.page_content} SOURCE: {'http://doi.org/'+d.metadata['doi'] if 'doi' in d.metadata and d.metadata['doi'] is not None else d.metadata['source']}"
    return [document_to_string(d) for d in results]