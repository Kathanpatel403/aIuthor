"""FastAPI application entrypoint."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from aiuthor import __version__
from aiuthor.api.routes import books as books_routes
from aiuthor.api.routes import evals as evals_routes
from aiuthor.api.routes import generate as generate_routes
from aiuthor.api.routes import memory as memory_routes
from aiuthor.api.routes import rag as rag_routes
from aiuthor.api.routes import traces as traces_routes
from aiuthor.api.routes import tone_variants as tone_variants_routes
from aiuthor.api.routes import chapter_insert as chapter_insert_routes
from aiuthor.api.routes import tests as tests_routes
from aiuthor.config.settings import get_settings
from aiuthor.observability.langsmith_setup import configure_langsmith_runtime_env
from aiuthor.paths import sample_books_dir

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
    app.include_router(
        books_routes.router,
        prefix=f"{settings.aiuthor_api_prefix}/books",
    )
    # Test C — tone variants for a single chapter
    app.include_router(
        tone_variants_routes.router,
        prefix=f"{settings.aiuthor_api_prefix}/books",
        tags=["Test C — Tone Variants"],
    )
    # Test D — chapter insertion with self-healing
    app.include_router(
        chapter_insert_routes.router,
        prefix=f"{settings.aiuthor_api_prefix}/books",
        tags=["Test D — Chapter Insert"],
    )
    # Audit Test Orchestrator
    app.include_router(
        tests_routes.router,
        prefix=f"{settings.aiuthor_api_prefix}/tests",
        tags=["Audit Tests"],
    )

    books_root = sample_books_dir()
    books_root.mkdir(parents=True, exist_ok=True)
    app.mount(
        f"{settings.aiuthor_api_prefix}/media/sample-books",
        StaticFiles(directory=str(books_root)),
        name="sample_books_media",
    )

    return app


app = create_app()
