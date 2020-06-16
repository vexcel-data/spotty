import re

from typing import List, Any

from spotty.commands.writers.abstract_output_writrer import AbstractOutputWriter
from spotty.providers.aws.deployment.project_resources.bucket.abstruct_bucket import AbstractBucketResource
from spotty.utils import random_string


class ProjectBucketResource(AbstractBucketResource):

    def __init__(self, project_name: str, region: str):
        super().__init__(region)
        self._bucket_name = None
        self._bucket_prefix = 'spotty-%s' % project_name.lower()

    def _find_bucket(self):
        res = self._s3.list_buckets()
        regex = re.compile('-'.join([self._bucket_prefix, '[a-z0-9]{12}', self._region]))
        buckets = [bucket['Name'] for bucket in res['Buckets'] if regex.match(bucket['Name']) is not None]

        if len(buckets) > 1:
            raise ValueError('Found several buckets in the same region: %s.' % ', '.join(buckets))

        bucket_name = buckets[0] if len(buckets) else False

        return bucket_name

    def get_or_create_bucket(self, output: AbstractOutputWriter, tags: List[Any], dry_run: bool = False):
        bucket_name = self._find_bucket()
        if not bucket_name:
            bucket_name = '-'.join([self._bucket_prefix, random_string(12), self._region])
            if not dry_run:
                # a fix for the boto3 issue: https://github.com/boto/boto3/issues/125
                if self._region == 'us-east-1':
                    self._s3.create_bucket(ACL='private', Bucket=bucket_name)
                else:
                    self._s3.create_bucket(ACL='private', Bucket=bucket_name,
                                           CreateBucketConfiguration={'LocationConstraint': self._region})
                self._s3.put_bucket_tagging(Bucket=bucket_name, Tagging={'TagSet': tags})
            output.write('Bucket "%s" was created.' % bucket_name)
        self._bucket_name = bucket_name
        return bucket_name

    @property
    def path_prefix(self) -> str:
        return '/'
