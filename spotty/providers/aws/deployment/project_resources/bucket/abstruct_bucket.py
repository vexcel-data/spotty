from abc import ABC, abstractmethod
import boto3

from spotty.commands.writers.abstract_output_writrer import AbstractOutputWriter

class AbstractBucketResource(ABC):

    def __init__(self, region: str):
        self._region = region
        self._s3 = boto3.client('s3', region_name=region)

    @abstractmethod
    def get_or_create_bucket(self, output: AbstractOutputWriter, tags: list, dry_run=False):
        raise NotImplementedError

    @property
    @abstractmethod
    def path_prefix(self):
        """
        Bucket path prefix.
        e.g. with '/' spotty data will be stored in bucket root
        with '/spotty/' it will be stored under spotty directory
        """
        raise NotImplementedError

