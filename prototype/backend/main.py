from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router as api_router
from app.session_api import router as session_api_router
from app.session_analysis import router as session_analysis_router

app = FastAPI(
    title="Language IDE API",
    description="API for Language IDE - Map-first Meaning Graph System",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Configuration
origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/v0")
app.include_router(session_api_router, prefix="/v0")
app.include_router(session_analysis_router, prefix="/v0") # Session-aware analysis

@app.get("/")
async def root():
    return {"message": "Language IDE API is running. Visit /docs for API documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
