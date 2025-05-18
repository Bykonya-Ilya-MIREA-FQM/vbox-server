import pydantic

ImageFile = pydantic.constr(pattern = r'^[a-zA-Z0-9](?:[a-zA-Z0-9_-]|\.?[a-zA-Z0-9_-])*\.iso$')
ImageName = pydantic.constr(pattern = r'^[a-zA-Z0-9](?:[a-zA-Z0-9_-]|\.?[a-zA-Z0-9_-])*$')
