from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from lipidmetabolism import Lipidmetabolism
from pathlib import Path
from longevitymap import Longevitymap
from coronary import Coronary
from thrombophilia import Thrombophilia
from module_intefrace import ModuleInterface
from disgenet import DiseaseGenNet

# disgenet_2020.sqlite could be downloaded here https://www.disgenet.org/downloads
diseaseGenNet = DiseaseGenNet(Path("data", "disgenet_2020.sqlite"))

longevitymap = Longevitymap(Path("data", "longevitymap.sqlite"))

modules:list[ModuleInterface] = [Lipidmetabolism(Path("data", "lipid_metabolism.sqlite")),
           longevitymap,
           Coronary(Path("data", "coronary.sqlite")),
           Thrombophilia(Path("data", "thrombophilia.sqlite")),
           diseaseGenNet]

app = FastAPI(title="Longevitymap REST",
    version="0.1",
    description="API server to handle queries to longevitymap REST.",
    debug=True)


@app.get("/")
def read_root():
    return "This is REST API for longavity map."


@app.get("/rsid_lookup/{rsid}")
def rsid_lookup(rsid:str):
    result = ""
    for module in modules:
        result += module.rsid_lookup(rsid)+"\n"
    return result


@app.get("/gene_lookup/{gene}")
def gene_lookup(gene:str):
    result = ""
    for module in modules:
        result += module.gene_lookup(gene)+"\n"
    return result


@app.get("/pathway_lookup/{pathway}")
def pathway_lookup(pathway:str):
    return longevitymap.pathway_lookup(pathway)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Longevity map REST API",
        version="0.1",
        description="",
        terms_of_service="https://agingkills.eu/terms/",
        routes=app.routes,
    )

    openapi_schema["servers"] = [{"url": "https://longevitymap.agingkills.eu"}, {"url": "http://localhost:8084"}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app,
                host="0.0.0.0",
                # host = "192.168.0.249",
                port = 8084
                )