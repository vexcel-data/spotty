from typing import List, Dict


class ContainerConfig(object):

    def __init__(self, container_config: dict):
        self._config = container_config

    @property
    def project_dir(self):
        return self._config['projectDir']

    @property
    def image(self):
        return self._config['image']

    @property
    def file(self):
        return self._config['file']

    @property
    def volume_mounts(self):
        return self._config['volumeMounts']

    @property
    def ports(self) -> List[int]:
        return list(set(self._config['ports']))

    @property
    def commands(self):
        return self._config['commands']

    @property
    def working_dir(self):
        """Working directory for the Docker container."""
        working_dir = self._config['workingDir']
        if not working_dir:
            working_dir = self._config['projectDir']

        return working_dir

    @property
    def runtime_parameters(self):
        return self._config['runtimeParameters']

    @property
    def build_args(self) -> Dict[str, str]:
        return {arg['name']: arg['value'] for arg in self._config.get('buildArgs', [])}
