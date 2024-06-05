import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from cloud.config import CORS_MIDDLEWARE_ALLOW_ORIGINS, SENTRY_SDK_URL


def add_cors_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_MIDDLEWARE_ALLOW_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def add_sentry_middleware(app: FastAPI) -> None:
    sentry_sdk.init(dsn=SENTRY_SDK_URL, traces_sample_rate=1.0)
    app.add_middleware(SentryAsgiMiddleware)
