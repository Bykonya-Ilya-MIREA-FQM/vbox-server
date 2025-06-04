import presentation.config
import domain.machines.models
import domain.machines
import fastapi
import typing
import uuid

def get_vboxapi(config: typing.Annotated[presentation.config.ApplicationConfig, fastapi.Depends(presentation.config.load_application_config)]) -> domain.machines.VirtualBoxApi:
    return domain.machines.VirtualBoxApi(
        advertised_host = config.advertised_host,
        machines_dir = config.machines_dir,
        storages_dir = config.storages_dir,
        images_dir = config.images_dir,
    )


router = fastapi.APIRouter()

@router.get('/machine', response_model = domain.machines.models.VirtualBoxApiResponse[list[uuid.UUID]])
def list_vms(vbox_api: typing.Annotated[domain.machines.VirtualBoxApi, fastapi.Depends(get_vboxapi)]) -> domain.machines.models.VirtualBoxApiResponse[list[uuid.UUID]]:
    return vbox_api.list_vms()
@router.get('/machine/{machine_uuid}', response_model = domain.machines.models.VirtualBoxApiResponse[domain.machines.models.FullMachineInfo])
def vm_info(vbox_api: typing.Annotated[domain.machines.VirtualBoxApi, fastapi.Depends(get_vboxapi)], machine_uuid: typing.Annotated[uuid.UUID, fastapi.Path()]) -> domain.machines.models.VirtualBoxApiResponse[domain.machines.models.FullMachineInfo]:
    return vbox_api.vm_info(vm_uuid = machine_uuid)

@router.post('/machine', response_model = domain.machines.models.VirtualBoxApiResponse[uuid.UUID])
def create_vm(vbox_api: typing.Annotated[domain.machines.VirtualBoxApi, fastapi.Depends(get_vboxapi)], machine_info: typing.Annotated[domain.machines.models.CreateMachineInfo, fastapi.Body()]) -> domain.machines.models.VirtualBoxApiResponse[uuid.UUID]:
    return vbox_api.create_vm(machine_info = machine_info)
@router.delete('/machine/{machine_uuid}', response_model = domain.machines.models.VirtualBoxApiResponse[None])
def delete_vm(vbox_api: typing.Annotated[domain.machines.VirtualBoxApi, fastapi.Depends(get_vboxapi)], machine_uuid: typing.Annotated[uuid.UUID, fastapi.Path()]) -> domain.machines.models.VirtualBoxApiResponse[None]:
    return vbox_api.delete_vm(vm_uuid = machine_uuid)

@router.post('/machine/{machine_uuid}/run_command', response_model = domain.machines.models.VirtualBoxApiResponse[None])
def run_vm_command(vbox_api: typing.Annotated[domain.machines.VirtualBoxApi, fastapi.Depends(get_vboxapi)], machine_uuid: typing.Annotated[uuid.UUID, fastapi.Path()], run_vm_command: typing.Annotated[domain.machines.models.RunVmCommand, fastapi.Body()]) -> domain.machines.models.VirtualBoxApiResponse[None]:
    return vbox_api.run_vm_command(vm_uuid = machine_uuid, run_vm_command_info = run_vm_command)
@router.post('/machine/{machine_uuid}/start', response_model = domain.machines.models.VirtualBoxApiResponse[domain.machines.models.VrdeConnectionInfo])
def start_vm(vbox_api: typing.Annotated[domain.machines.VirtualBoxApi, fastapi.Depends(get_vboxapi)], machine_uuid: typing.Annotated[uuid.UUID, fastapi.Path()]) -> domain.machines.models.VirtualBoxApiResponse[None]:
    return vbox_api.start_vm(vm_uuid = machine_uuid)
@router.post('/machine/{machine_uuid}/stop', response_model = domain.machines.models.VirtualBoxApiResponse[None])
def stop_vm(vbox_api: typing.Annotated[domain.machines.VirtualBoxApi, fastapi.Depends(get_vboxapi)], machine_uuid: typing.Annotated[uuid.UUID, fastapi.Path()]) -> domain.machines.models.VirtualBoxApiResponse[None]:
    return vbox_api.stop_vm(vm_uuid = machine_uuid)
