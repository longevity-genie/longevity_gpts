from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import clinical_trails_router
from fastapi.openapi.utils import get_openapi


app = FastAPI(debug=True)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(clinical_trails_router.clinical_trails_router)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Clinical trails REST API",
        version="0.1",
        description="",
        terms_of_service="https://agingkills.eu/terms/",
        routes=app.routes,
    )

    openapi_schema["servers"] = [{"url": "https://clinical-trials.longevity-genie.info"}, {"url": "https://localhost:8085"}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,
                host="0.0.0.0",
                port=8085
                )