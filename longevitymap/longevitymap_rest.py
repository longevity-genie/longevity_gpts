from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from lipidmetabolism import Lipidmetabolism
from pathlib import Path

modules = [Lipidmetabolism(Path("data", "lipid_metabolism.sqlite"))]

app = FastAPI(title="Lomgevitymap REST",
    version="0.1",
    description="API server to handle queries to lomgevitymap REST.",
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
    # openapi_schema["externalDocs"] = ExternalDocumentation(
    #     description="Privacy Policy",
    #     url="https://agingkills.eu/privacy-policy"
    # ).dict()
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