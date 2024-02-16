from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from clinical_trails_router import clinical_trails_router


app = FastAPI(debug=True)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(clinical_trails_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,
                host="0.0.0.0",
                port=8085
                )