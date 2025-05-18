import pydantic

ConfigFile = pydantic.constr(pattern = r'^[a-zA-Z0-9](?:[a-zA-Z0-9_-]|\.?[a-zA-Z0-9_-])*\.json$')
ConfigName = pydantic.constr(pattern = r'^[a-zA-Z0-9](?:[a-zA-Z0-9_-]|\.?[a-zA-Z0-9_-])*$')
