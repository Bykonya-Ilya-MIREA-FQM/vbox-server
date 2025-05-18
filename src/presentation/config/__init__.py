import functools
import pydantic
import typing
import os

class ApplicationConfig(pydantic.BaseModel):
    advertised_host: str
    machines_dir: str
    storages_dir: str
    configs_dir: str
    images_dir: str

@functools.lru_cache(maxsize = 1, typed = 1)
@pydantic.validate_call(validate_return = True)
def load_application_config() -> ApplicationConfig:
    return ApplicationConfig(
        advertised_host = os.environ['VBOX_SERVER__ADVERTISED_HOST'],
        machines_dir = os.environ['VBOX_SERVER__MACHINES_DIR'],
        storages_dir = os.environ['VBOX_SERVER__STORAGES_DIR'],
        configs_dir = os.environ['VBOX_SERVER__CONFIGS_DIR'],
        images_dir = os.environ['VBOX_SERVER__IMAGES_DIR'],
    )
