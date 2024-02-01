from pathlib import Path

from fastapi import APIRouter
from fastapi.openapi.utils import get_openapi

from genetics.disgenet import DiseaseGenNet
from genetics.coronary import Coronary
from genetics.lipidmetabolism import Lipidmetabolism
from genetics.longevitymap import Longevitymap
from genetics.module_intefrace import ModuleInterface
from genetics.thrombophilia import Thrombophilia
from genetics.dna_sequencing import DnaSequencing

# disgenet_2020.sqlite could be downloaded here https://www.disgenet.org/downloads
diseaseGenNet = DiseaseGenNet(Path("genetics","data", "disgenet_2020.sqlite"), Path("genetics","data", "disease_names.csv"))

longevitymap = Longevitymap(Path("genetics","data", "longevitymap.sqlite"))

dna_sequencing = DnaSequencing(Path("genetics","data", "dna_sequencing.txt"))

modules: list[ModuleInterface] = [Lipidmetabolism(Path("genetics", "data", "lipid_metabolism.sqlite")),
           longevitymap,
           Coronary(Path("genetics", "data", "coronary.sqlite")),
           Thrombophilia(Path("genetics", "data", "thrombophilia.sqlite")),
           dna_sequencing,
           diseaseGenNet]

genetics_router = APIRouter()


@genetics_router.get("/")
def read_root():
    return "This is REST API for longavity map."


@genetics_router.get("/rsid_lookup/{rsid}", description="Returns information about varinat by its rsId.")
def rsid_lookup(rsid:str):
    result = ""
    for module in modules:
        result += module.rsid_lookup(rsid)+"\n"
    return result


@genetics_router.get("/gene_lookup/{gene}", description="Returns information about gene by its symbol.")
def gene_lookup(gene:str):
    result = ""
    for module in modules:
        result += module.gene_lookup(gene)+"\n"
    return result


@genetics_router.get("/pathway_lookup/{pathway}", description="Returns information about genetic pathway.")
def pathway_lookup(pathway:str):
    return longevitymap.pathway_lookup(pathway)


@genetics_router.get("/disease_lookup/{disease}", description="Returns information about disease by its name.")
def disease_lookup(disease:str):
    return diseaseGenNet.disease_lookup(disease)

@genetics_router.get("/sequencing_info/")
def  sequencing_info():
    return  dna_sequencing.sequencing_info()

def custom_openapi():
    if genetics_router.openapi_schema:
        return genetics_router.openapi_schema
    openapi_schema = get_openapi(
        title="Longevity map REST API",
        version="0.1",
        description="",
        terms_of_service="https://agingkills.eu/terms/",
        routes=genetics_router.routes,
    )

    openapi_schema["servers"] = [{"url": "https://longevitymap.agingkills.eu"}, {"url": "http://localhost:8084"}]
    genetics_router.openapi_schema = openapi_schema
    return genetics_router.openapi_schema

genetics_router.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(genetics_router,
                host="0.0.0.0",
                # host = "192.168.0.249",
                port = 8084
                )