"""Shared app factory for analysis services."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_analysis_app(title: str, engine_name: str, is_available_fn) -> FastAPI:
    """Create a FastAPI app with standard CORS + health endpoint."""
    app = FastAPI(title=title, docs_url="/api/docs")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    @app.get("/health")
    async def health():
        available = await is_available_fn()
        return {"status": "ok" if available else "degraded", "engine": engine_name}

    return app
