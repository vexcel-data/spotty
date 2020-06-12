from spotty.commands.writers.abstract_output_writrer import AbstractOutputWriter
from spotty.providers.aws.deployment.project_resources.bucket.abstruct_bucket import AbstractBucketResource


class ExistingBucketResource(AbstractBucketResource):

    def __init__(self, bucket_name: str, project_name: str, region: str):
        super().__init__(region)
        self._bucket_name = bucket_name
        self._project_name = project_name

    def get_or_create_bucket(self, output: AbstractOutputWriter, tags: list, dry_run=False):
        return self._bucket_name

    @property
    def path_prefix(self):
        return f'/spotty/{self._project_name}/'
