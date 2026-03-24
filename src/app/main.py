from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import authrouter as api_auth_router
from api import router as api_router
from api.exception_handlers import EXCEPTION_HANDLERS
from app.core.logging import setup_logging
from common.logging_middleware import LoggingMiddleware


setup_logging()
app = FastAPI(
    title="POC Cars API",
    openapi_url="/v1/poc/openapi.json",
    exception_handlers=EXCEPTION_HANDLERS,
    swagger_ui_parameters={
        "filter": True,  # Adds search/filter box
        "docExpansion": "none",  # Keeps endpoints collapsed by default
        "tagsSorter": "alpha",  # Sorts tags alphabetically
        "operationsSorter": "alpha",  # Sorts operations alphabetically
    },
)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/v1/poc")
app.include_router(api_auth_router, prefix="")


@app.get("/")
def health_check():
    return {"status": "API running"}

