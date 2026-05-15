"""FastAPI application entrypoint."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aiuthor import __version__
from aiuthor.api.routes import evals as evals_routes
from aiuthor.api.routes import generate as generate_routes
from aiuthor.api.routes import memory as memory_routes
from aiuthor.api.routes import rag as rag_routes
from aiuthor.api.routes import traces as traces_routes
from aiuthor.config.settings import get_settings
from aiuthor.observability.langsmith_setup import configure_langsmith_runtime_env

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_langsmith_runtime_env()
    settings = get_settings()
    if settings.aiuthor_memory_backend == "redis":
        logger.warning(
            "AIUTHOR_MEMORY_BACKEND=redis is not implemented yet; using in-memory store."
        )
    logger.info("AIuthor %s starting (%s)", __version__, settings.aiuthor_env)
    yield
    logger.info("AIuthor shutdown complete")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="AIuthor API",
        version=__version__,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok", "service": "aiuthor", "version": __version__}

    @app.get(f"{settings.aiuthor_api_prefix}/health", tags=["system"])
    def api_health() -> dict[str, str]:
        return {"status": "ok", "service": "aiuthor", "version": __version__}

    app.include_router(
        memory_routes.router,
        prefix=f"{settings.aiuthor_api_prefix}/memory",
    )
    app.include_router(
        rag_routes.router,
        prefix=f"{settings.aiuthor_api_prefix}/rag",
    )
    app.include_router(
        generate_routes.router,
        prefix=f"{settings.aiuthor_api_prefix}/generate",
    )
    app.include_router(
        traces_routes.router,
        prefix=f"{settings.aiuthor_api_prefix}/traces",
    )
    app.include_router(
        evals_routes.router,
        prefix=f"{settings.aiuthor_api_prefix}/evals",
    )

    return app


app = create_app()
