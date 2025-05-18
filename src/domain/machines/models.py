import pydantic


class VBoxManageCallResult(pydantic.BaseModel):
    args: list[str]
    status: int
    stdout: str
    stderr: str

class LogEntry(pydantic.BaseModel):
    stage: pydantic.constr(min_length = 1) # type: ignore
    call: VBoxManageCallResult

class VirtualBoxApiResponse[GenericPayloadType](pydantic.BaseModel):
    payload: GenericPayloadType
    logs: list[LogEntry]

class VirtualBoxApiError(Exception):
    @pydantic.validate_call(validate_return = True)
    def __init__(self, error_info: VBoxManageCallResult, stage: str, message: str = '') -> None:
        self.__error_info: VBoxManageCallResult = error_info
        self.__stage: str = stage

    @property
    def error_info(self) -> VBoxManageCallResult:
        return self.__error_info
    @property
    def stage(self) -> str:
        return self.__stage



class VrdeConnectionInfo(pydantic.BaseModel):
    host: pydantic.constr(min_length = 0) # type: ignore
    port: pydantic.conint(ge = 0, le = 65535) # type: ignore

class CreateMachineInfo(pydantic.BaseModel):
    class HardwareInfo(pydantic.BaseModel):
        cpu_count: pydantic.PositiveInt
        memory_mb: pydantic.conint(gt = 0, multiple_of = 128) # type: ignore
        vram_mb: pydantic.conint(gt = 0, multiple_of = 16) # type: ignore
    class VrdeCredentialsInfo(pydantic.BaseModel):
        username: pydantic.constr(min_length = 1, max_length = 255) # type: ignore
        password: pydantic.constr(min_length = 8, max_length = 255) # type: ignore
    class DriveInfo(pydantic.BaseModel):
        size_gb: pydantic.PositiveInt

    os_type: str
    template: str
    drive: DriveInfo
    hardware: HardwareInfo
    vrde_credentials: VrdeCredentialsInfo

class FullMachineInfo(pydantic.BaseModel):
    is_online: bool
    vrde_connection: VrdeConnectionInfo
