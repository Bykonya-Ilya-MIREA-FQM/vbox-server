from domain.images.models import ImageFile, ImageName
import pydantic
import abc
import os


class AbstractImageRepository(abc.ABC):
    @abc.abstractmethod
    @pydantic.validate_call(validate_return = True)
    def list_images(self) -> list[ImageName]:
        raise NotImplementedError(f'{type(self)}.list_images')


class LocalImageRepository(AbstractImageRepository):
    @pydantic.validate_call(validate_return = True)
    def __init__(self, images_dir: str) -> None:
        self.__images_dir: str = images_dir
    @pydantic.validate_call(validate_return = True)
    def list_images(self) -> list[ImageName]:
        configs: list[ImageName] = []
        for filename in os.listdir(self.__images_dir):
            try:
                configs.append(pydantic.RootModel[ImageName](root = pydantic.RootModel[ImageFile](root = filename).root[0:-4]).root)
            except Exception:
                pass
        return configs
