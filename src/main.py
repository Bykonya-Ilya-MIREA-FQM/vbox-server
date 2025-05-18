from contextlib import asynccontextmanager
import presentation.api.v1.machines
import presentation.api.v1.configs
import presentation.api.v1.images
import presentation.config
import domain.machines.models
import fastapi.responses
import fastapi
import typing

@asynccontextmanager
async def application_lifespan(app: fastapi.FastAPI) -> typing.Generator[None]:
    yield print(presentation.config.load_application_config())

app = fastapi.FastAPI(lifespan = application_lifespan)
app.include_router(router = presentation.api.v1.machines.router, prefix = '/api/v1')
app.include_router(router = presentation.api.v1.configs.router, prefix = '/api/v1')
app.include_router(router = presentation.api.v1.images.router, prefix = '/api/v1')

@app.exception_handler(domain.machines.models.VirtualBoxApiError)
async def unicorn_exception_handler(request: fastapi.Request, exc: domain.machines.models.VirtualBoxApiError):
    return fastapi.responses.JSONResponse(
        status_code = 500,
        content = {
            'stage': exc.stage,
            'call': exc.error_info.model_dump()
        },
    )
