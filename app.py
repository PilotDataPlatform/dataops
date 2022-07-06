# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License along with this program. If not,
# see http://www.gnu.org/licenses/.

from functools import partial

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from api.routes import api_router
from api.routes import api_router_v2
from config import Settings
from config import get_settings
from dependencies import get_redis
from resources.db import get_db_engine


def create_app() -> FastAPI:
    """Initialize and configure the application."""

    settings = get_settings()

    app = FastAPI(
        title='Dataops Service',
        description='Dataops',
        docs_url='/v1/api-doc',
        version=settings.VERSION,
    )

    setup_routers(app)
    return app


def setup_routers(app: FastAPI) -> None:
    """Configure the application routers."""

    app.include_router(api_router, prefix='/v1')
    app.include_router(api_router_v2, prefix='/v2')


def setup_middlewares(app: FastAPI) -> None:
    """Configure the application middlewares."""

    app.add_middleware(
        CORSMiddleware,
        allow_origins='*',
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )


def setup_dependencies(app: FastAPI, settings: Settings) -> None:
    """Perform dependencies setup/teardown at the application startup/shutdown events."""

    app.add_event_handler('startup', partial(startup_event, settings))


async def startup_event(settings: Settings) -> None:
    """Initialise dependencies at the application startup event."""

    await get_redis(settings=settings)


def setup_exception_handlers(app: FastAPI) -> None:
    """Configure the application exception handlers."""

    app.add_exception_handler(Exception, global_exception_handler)


def global_exception_handler(request: Request, exception: Exception) -> JSONResponse:
    """Return the default response structure for all unhandled exceptions."""

    return JSONResponse(status_code=500, content={'error_msg': 'Internal Server Error'})


async def _initialize_instrument_app(app: FastAPI, settings: Settings) -> None:
    """Instrument the application with OpenTelemetry tracing."""

    tracer_provider = TracerProvider(resource=Resource.create({SERVICE_NAME: settings.APP_NAME}))
    trace.set_tracer_provider(tracer_provider)

    FastAPIInstrumentor.instrument_app(app)
    HTTPXClientInstrumentor().instrument()
    LoggingInstrumentor().instrument()

    db = await get_db_engine()
    SQLAlchemyInstrumentor().instrument(engine=db.sync_engine, service=settings.APP_NAME)

    jaeger_exporter = JaegerExporter(
        agent_host_name=settings.OPEN_TELEMETRY_HOST, agent_port=settings.OPEN_TELEMETRY_PORT
    )

    tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))


async def on_startup_event(app: FastAPI, settings: Settings) -> None:
    setup_middlewares(app)
    setup_dependencies(app, settings)
    setup_exception_handlers(app)

    if settings.OPEN_TELEMETRY_ENABLED:
        await _initialize_instrument_app(app, settings)


app = create_app()
settings = get_settings()


@app.on_event('startup')
async def startup() -> None:
    await on_startup_event(app, settings)
