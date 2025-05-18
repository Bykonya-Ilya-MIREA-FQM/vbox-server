import presentation.config
import domain.machines.models
import domain.configs.models
import domain.configs
import fastapi
import typing

def get_config_repository(config: typing.Annotated[presentation.config.ApplicationConfig, fastapi.Depends(presentation.config.load_application_config)]) -> domain.configs.AbstractConfigRepository:
    return domain.configs.LocalConfigRepository(
        configs_dir = config.configs_dir
    )


router = fastapi.APIRouter()

@router.get('/config')
async def list_configs(configs: typing.Annotated[domain.configs.AbstractConfigRepository, fastapi.Depends(get_config_repository)]) -> list[domain.configs.models.ConfigName]:
    return configs.list_configs()

@router.get('/config/{config_name}')
async def load_config(configs: typing.Annotated[domain.configs.AbstractConfigRepository, fastapi.Depends(get_config_repository)], config_name: typing.Annotated[domain.configs.models.ConfigName, fastapi.Path()]) -> domain.machines.models.CreateMachineInfo:
    return configs.load_config(config = config_name)
