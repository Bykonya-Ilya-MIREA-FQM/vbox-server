from domain.configs.models import ConfigFile, ConfigName
from domain.machines.models import CreateMachineInfo
import pydantic
import json
import abc
import os

class AbstractConfigRepository(abc.ABC):
    @abc.abstractmethod
    @pydantic.validate_call(validate_return = True)
    def list_configs(self) -> list[ConfigName]:
        raise NotImplementedError(f'{type(self)}.list_configs')
    @abc.abstractmethod
    @pydantic.validate_call(validate_return = True)
    def load_config(self, config: ConfigName) -> CreateMachineInfo:
        raise NotImplementedError(f'{type(self)}.load_config')

class LocalConfigRepository(AbstractConfigRepository):
    @pydantic.validate_call(validate_return = True)
    def __init__(self, configs_dir: str) -> None:
        self.__configs_dir: str = configs_dir
    @pydantic.validate_call(validate_return = True)
    def list_configs(self) -> list[ConfigName]:
        configs: list[ConfigName] = []
        for filename in os.listdir(self.__configs_dir):
            try:
                configs.append(pydantic.RootModel[ConfigName](root = pydantic.RootModel[ConfigFile](root = filename).root[0:-5]).root)
            except Exception:
                pass
        return configs
    @pydantic.validate_call(validate_return = True)
    def load_config(self, config: ConfigName) -> CreateMachineInfo:
        return CreateMachineInfo.model_validate(obj = json.load(open(file = f'{self.__configs_dir}/{config}.json', mode = 'r')))
