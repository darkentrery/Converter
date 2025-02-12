from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status, responses
from fastapi.openapi.utils import get_openapi
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from starlette.middleware.cors import CORSMiddleware

from app import version, exc, entity
from app.api import format, user, converter
from app.config import config
from app.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup(app)
    logger.info('Application startup!')
    yield
    await shutdown(app)
    logger.info('Application shutdown!')


def create_app(is_test: bool = False) -> FastAPI:
    app = FastAPI(
        title=version.APP_FULLNAME,
        debug=config.debug,
        docs_url=f'/{version.APP_NAME}/v1/docs',
        openapi_url=f"/{version.APP_NAME}/v1/openapi.json",
        lifespan=lifespan
    )
    app.state.is_test = is_test

    @app.exception_handler(exc.AppError)
    async def on_app_error(_: Request, e: exc.AppError):
        code = status.HTTP_500_INTERNAL_SERVER_ERROR

        match type(e):
            case exc.NotFoundError:
                code = status.HTTP_404_NOT_FOUND
            case exc.AlreadyExists:
                code = status.HTTP_409_CONFLICT

        return responses.JSONResponse(
            content={"detail": str(e)},
            status_code=code,
        )

    for dep in [format, user, converter]:
        router = getattr(dep, 'router')
        app.include_router(router, prefix=f'/{version.APP_NAME}/v1')

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


async def startup(app: FastAPI):
    # Postgres
    engine = create_async_engine(config.async_dsn)
    test_connection = await engine.connect()
    await test_connection.close()
    app.state.pg_async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

    if not app.state.is_test:
        pass


async def shutdown(app: FastAPI):
    if not app.state.is_test:
        pass


def custom_openapi(app: FastAPI) -> dict:
    auth_method = 'OptionalHTTPBearer'
    auth_scheme = {
        "securitySchemes": {
            auth_method: {
                "type": "http",
                "scheme": "bearer"
            }
        }
    }
    openapi_schema = get_openapi(
        title=version.APP_FULLNAME,
        version="3.0.0",
        routes=app.routes,
        openapi_version="3.0.0"
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://www.tadviser.ru/images/4/40/Cortel_logo-31%D0%BC%D0%B0%D1%80%D1%822022.png"
    }
    for path, value in openapi_schema['paths'].items():
        for method in value.keys():
            openapi_schema['paths'][path][method].update(
                {
                    "security": [{auth_method: []}]
                }
            )
    # openapi_schema['components'].update(auth_scheme)
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app = create_app()
custom_openapi(app)
