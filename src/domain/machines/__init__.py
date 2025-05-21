from . models import VBoxManageCallResult, LogEntry, VirtualBoxApiResponse, VirtualBoxApiError, VrdeConnectionInfo, CreateMachineInfo, FullMachineInfo
import subprocess
import pydantic
import hashlib
import socket
import uuid


class VirtualBoxApi:
    @pydantic.validate_call(validate_return = True)
    def __init__(self, machines_dir: str, storages_dir: str, images_dir: str, advertised_host: str, vboxmanage_bin: str = 'VBoxManage') -> None:
        self.__advertised_host: str = advertised_host
        self.__vboxmanage_bin: str = vboxmanage_bin
        self.__machines_dir: str = machines_dir
        self.__storages_dir: str = storages_dir
        self.__images_dir: str = images_dir

    @pydantic.validate_call(validate_return = True)
    def __get_free_port(self, host: str) -> int:
        sock = socket.socket()
        sock.bind((host, 0))
        (host, port) = sock.getsockname()
        sock.close()
        return port
    @pydantic.validate_call(validate_return = True)
    def __execute_call(self, args: list[str]) -> VBoxManageCallResult:
        raw_result = subprocess.run(args = [self.__vboxmanage_bin] + args, capture_output = True)
        return VBoxManageCallResult(
            status = raw_result.returncode,
            stdout = raw_result.stdout,
            stderr = raw_result.stderr,
            args = raw_result.args,
        )



    @pydantic.validate_call(validate_return = True)
    def list_vms(self) -> VirtualBoxApiResponse[list[uuid.UUID]]:
        result = self.__execute_call(args = ['list', 'vms'])
        if result.status != 0:
            raise VirtualBoxApiError(error_info = result, stage = 'list_vms.root')

        return VirtualBoxApiResponse[list[uuid.UUID]](
            payload = [uuid.UUID(line[-37:-1]) for line in result.stdout.split(sep = '\r\n') if len(line) > 0],
            logs = [LogEntry(stage = 'list_vms.root', call = result)]
        )
    @pydantic.validate_call(validate_return = True)
    def vm_info(self, vm_uuid: uuid.UUID) -> VirtualBoxApiResponse[FullMachineInfo]:
        get_raw_vm_info_result = self.__execute_call(args = ['showvminfo', str(vm_uuid), '--machinereadable'])
        if get_raw_vm_info_result.status != 0:
            raise VirtualBoxApiError(error_info = get_raw_vm_info_result, stage = 'vm_info.get_raw_vm_info')
        raw_vm_info_dict: dict[str, str] = dict()
        for line in get_raw_vm_info_result.stdout.split(sep = '\r\n'):
            if len(chunks := line.split('=', maxsplit = 1)) == 2:
                raw_vm_info_dict[chunks[0]] = chunks[1]

        return VirtualBoxApiResponse[FullMachineInfo](
            payload = FullMachineInfo(
                is_online = (raw_vm_info_dict['VMState'] == '"running"'),
                vrde_connection = VrdeConnectionInfo(
                    host = raw_vm_info_dict.get('vrdeaddress', '""')[1:-1], 
                    port = int(raw_vm_info_dict.get('vrdeports', '"0"')[1:-1])
                )
            ),
            logs = [LogEntry(stage = 'vm_info.get_raw_vm_info', call = get_raw_vm_info_result)]
        )

    @pydantic.validate_call(validate_return = True)
    def create_vm(self, machine_info: CreateMachineInfo) -> VirtualBoxApiResponse[uuid.UUID]:
        vm_uuid = uuid.uuid4()

        create_machine_result = self.__execute_call(args = ['createvm', '--name', str(vm_uuid), '--uuid', str(vm_uuid), '--ostype', machine_info.os_type, '--basefolder', self.__machines_dir, '--register'])
        if create_machine_result.status != 0:
            raise VirtualBoxApiError(error_info = create_machine_result, stage = 'create_vm.create_machine')
        create_sata_controller_result = self.__execute_call(args = ['storagectl', str(vm_uuid), '--name', 'SATA', '--add', 'sata'])
        if create_sata_controller_result.status != 0:
            raise VirtualBoxApiError(error_info = create_sata_controller_result, stage = 'create_vm.create_sata_controller')
        create_ide_controller_result = self.__execute_call(args = ['storagectl', str(vm_uuid), '--name', 'IDE', '--add', 'ide'])
        if create_ide_controller_result.status != 0:
            raise VirtualBoxApiError(error_info = create_ide_controller_result, stage = 'create_vm.create_ide_controller')
        
        setup_internal_hardware_result = self.__execute_call(args = ['modifyvm', str(vm_uuid), '--cpus', str(machine_info.hardware.cpu_count), '--memory', str(machine_info.hardware.memory_mb), '--vram', str(machine_info.hardware.vram_mb), '--graphicscontroller', 'vboxsvga', '--accelerate-3d', 'on'])
        if setup_internal_hardware_result.status != 0:
            raise VirtualBoxApiError(error_info = setup_internal_hardware_result, stage = 'create_vm.setup_internal_hardware')
        setup_external_hardware_result = self.__execute_call(args = ['modifyvm', str(vm_uuid), '--monitor-count', '1', '--mouse', 'usb', '--keyboard', 'usb'])
        if setup_external_hardware_result.status != 0:
            raise VirtualBoxApiError(error_info = setup_external_hardware_result, stage = 'create_vm.setup_external_hardware')
        setup_video_fps_result = self.__execute_call(args = ['modifyvm', str(vm_uuid), '--recording-video-fps', '60'])
        if setup_video_fps_result.status != 0:
            raise VirtualBoxApiError(error_info = setup_video_fps_result, stage = 'create_vm.setup_video_fps')
        
        setup_vrde_settings_result = self.__execute_call(args = ['modifyvm', str(vm_uuid), '--vrde', 'on', '--vrdeauthtype', 'external', '--vrdevideochannel', 'on', '--vrdevideochannelquality', '100'])
        if setup_vrde_settings_result.status != 0:
            raise VirtualBoxApiError(error_info = setup_vrde_settings_result, stage = 'create_vm.setup_vrde_settings')
        setup_vrde_credentials_result = self.__execute_call(args = ['setextradata', str(vm_uuid), f'VBoxAuthSimple/users/{machine_info.vrde_credentials.username}', hashlib.sha256(machine_info.vrde_credentials.password.encode('utf-8')).hexdigest()])
        if setup_vrde_credentials_result.status != 0:
            raise VirtualBoxApiError(error_info = setup_vrde_credentials_result, stage = 'create_vm.setup_vrde_credentials_result')
        
        attach_image_result = self.__execute_call(args = ['storageattach', str(vm_uuid), '--storagectl', 'IDE', '--port', '1', '--device', '0', '--type', 'dvddrive', '--medium', f'{self.__images_dir}/{machine_info.template}.iso'])
        if attach_image_result.status != 0:
            raise VirtualBoxApiError(error_info = attach_image_result, stage = 'create_vm.attach_image')
        create_drive_result = self.__execute_call(args = ['createhd', '--filename', f'{self.__storages_dir}/{vm_uuid}.vdi', '--size', str(machine_info.drive.size_gb * 1024 * 1024), '--format', 'VDI'])
        if create_drive_result.status != 0:
            raise VirtualBoxApiError(error_info = create_drive_result, stage = 'create_vm.create_drive')
        attach_drive_result = self.__execute_call(args = ['storageattach', str(vm_uuid), '--storagectl', 'SATA', '--port', '0', '--device', '0', '--type', 'hdd', '--medium', f'{self.__storages_dir}/{vm_uuid}.vdi'])
        if attach_drive_result.status != 0:
            raise VirtualBoxApiError(error_info = attach_drive_result, stage = 'create_vm.attach_drive')

        return VirtualBoxApiResponse[uuid.UUID](
            payload = vm_uuid,
            logs = [
                LogEntry(stage = 'create_vm.create_machine_result', call = create_machine_result),
                LogEntry(stage = 'create_vm.create_sata_controller_result', call = create_sata_controller_result),
                LogEntry(stage = 'create_vm.create_ide_controller_result', call = create_ide_controller_result),
                LogEntry(stage = 'create_vm.setup_internal_hardware_result', call = setup_internal_hardware_result),
                LogEntry(stage = 'create_vm.setup_external_hardware_result', call = setup_external_hardware_result),
                LogEntry(stage = 'create_vm.setup_video_fps_result', call = setup_video_fps_result),
                LogEntry(stage = 'create_vm.setup_vrde_settings_result', call = setup_vrde_settings_result),
                LogEntry(stage = 'create_vm.setup_vrde_credentials_result', call = setup_vrde_credentials_result),
                LogEntry(stage = 'create_vm.attach_image_result', call = attach_image_result),
                LogEntry(stage = 'create_vm.create_drive_result', call = create_drive_result),
                LogEntry(stage = 'create_vm.attach_drive_result', call = attach_drive_result),
            ]
        )
    @pydantic.validate_call(validate_return = True)
    def delete_vm(self, vm_uuid: uuid.UUID) -> VirtualBoxApiResponse[None]:
        result = self.__execute_call(args = ['unregistervm', str(vm_uuid), '--delete'])
        if result.status != 0:
            raise VirtualBoxApiError(error_info = result, stage = 'delete_vm.root')

        return VirtualBoxApiResponse[None](
            payload = None, logs = [LogEntry(stage = 'delete_vm.root', call = result)]
        )
    @pydantic.validate_call(validate_return = True)
    def start_vm(self, vm_uuid: uuid.UUID) -> VirtualBoxApiResponse[VrdeConnectionInfo]:
        get_vm_info_result = self.vm_info(vm_uuid = vm_uuid)
        if get_vm_info_result.payload.is_online:
            return VirtualBoxApiResponse[VrdeConnectionInfo](
                payload = get_vm_info_result.payload.vrde_connection,
                logs = get_vm_info_result.logs
            )

        get_vm_info_result.payload.vrde_connection.host = self.__advertised_host
        get_vm_info_result.payload.vrde_connection.port = self.__get_free_port(host = get_vm_info_result.payload.vrde_connection.host)
        setup_vrde_network_settings_result = self.__execute_call(args = ['modifyvm', str(vm_uuid), '--vrdeaddress', get_vm_info_result.payload.vrde_connection.host, '--vrdeport', str(get_vm_info_result.payload.vrde_connection.port)])
        if setup_vrde_network_settings_result.status != 0:
            raise VirtualBoxApiError(error_info = setup_vrde_network_settings_result, stage = 'start_vm.setup_vrde_network_settings')
        
        start_machine_result = self.__execute_call(args = ['startvm', str(vm_uuid), '--type', 'headless'])
        if start_machine_result.status != 0 and start_machine_result.status != 1: # return 1 where machine already run
            raise VirtualBoxApiError(error_info = start_machine_result, stage = 'start_vm.start_machine')

        return VirtualBoxApiResponse[VrdeConnectionInfo](
            payload = get_vm_info_result.payload.vrde_connection,
            logs = get_vm_info_result.logs + [
                LogEntry(stage = 'start_vm.setup_vrde_network_settings', call = setup_vrde_network_settings_result),
                LogEntry(stage = 'start_vm.start_machine', call = start_machine_result),
            ]
        )
    @pydantic.validate_call(validate_return = True)
    def stop_vm(self, vm_uuid: uuid.UUID) -> VirtualBoxApiResponse[None]:
        result = self.__execute_call(args = ['controlvm', str(vm_uuid), 'poweroff'])
        if result.status != 0 and result.status != 1: # return 1 where machine already stop
            raise VirtualBoxApiError(error_info = result, stage = 'stop_vm.root')

        return VirtualBoxApiResponse[None](
            payload = None, logs = [LogEntry(stage = 'stop_vm.root', call = result)]
        )
