import presentation.config
import domain.images.models
import domain.images
import fastapi
import typing

def get_image_repository(config: typing.Annotated[presentation.config.ApplicationConfig, fastapi.Depends(presentation.config.load_application_config)]) -> domain.images.AbstractImageRepository:
    return domain.images.LocalImageRepository(
        images_dir = config.images_dir
    )


router = fastapi.APIRouter()

@router.get('/image', response_model = list[domain.images.models.ImageName])
async def list_images(images: typing.Annotated[domain.images.AbstractImageRepository, fastapi.Depends(get_image_repository)]) -> list[domain.images.models.ImageName]:
    return images.list_images()
