from spotty.deployment.abstract_instance_volume import AbstractInstanceVolume
from spotty.providers.aws.config.validation import validate_efs_volume_parameters


class EfsVolume(AbstractInstanceVolume):

    def __init__(self, volume_config: dict):
        self._name = volume_config['name']
        self._params = validate_efs_volume_parameters(volume_config['parameters'])

    @property
    def file_system_id(self):
        return self._params['fileSystemId']

    @property
    def mount_target_sg_id(self):
        return self._params['mountTargetSgId']

    @property
    def title(self):
        return 'EFS'

    @property
    def name(self):
        return self._name

    @property
    def mount_dir(self) -> str:
        return self._params['mountDir']

    @property
    def deletion_policy_title(self) -> str:
        return 'retain'
