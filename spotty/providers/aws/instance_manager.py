from spotty.commands.writers.abstract_output_writrer import AbstractOutputWriter
from spotty.errors.instance_not_running import InstanceNotRunningError
from spotty.providers.aws.config.instance_config import InstanceConfig
from spotty.providers.aws.deployment.ami_deployment import AmiDeployment
from spotty.providers.aws.deployment.instance_deployment import InstanceDeployment
from spotty.providers.aws.helpers.download import download_from_s3_to_local, upload_from_instance_to_s3
from spotty.providers.aws.helpers.sync import sync_project_with_s3, sync_instance_with_s3
from spotty.providers.abstract_instance_manager import AbstractInstanceManager
from spotty.utils import render_table


class InstanceManager(AbstractInstanceManager):

    @property
    def instance_deployment(self) -> InstanceDeployment:
        """Returns an instance deployment manager."""
        return InstanceDeployment(self.project_config.project_name, self.instance_config)

    @property
    def ami_deployment(self) -> AmiDeployment:
        """Returns an AMI deployment manager."""
        return AmiDeployment(self.project_config.project_name, self.instance_config)

    def _get_instance_config(self, config: dict) -> InstanceConfig:
        """Validates the instance config and returns an InstanceConfig object."""
        return InstanceConfig(config)

    @property
    def instance_config(self) -> InstanceConfig:
        """This property is redefined just for a correct type hinting."""
        return self._instance_config

    def is_running(self):
        """Checks if the instance is running."""
        return bool(self.instance_deployment.get_instance())

    def start(self, output: AbstractOutputWriter, dry_run=False):
        deployment = self.instance_deployment

        if not dry_run:
            # check if the instance is already running
            instance = deployment.get_instance()
            if instance:
                print('Instance is already running. Are you sure you want to restart it?')
                res = input('Type "y" to confirm: ')
                if res != 'y':
                    raise ValueError('The operation was cancelled.')

                # terminating the instance to make EBS volumes available
                output.write('Terminating the instance...')
                instance.terminate()
                instance.wait_instance_terminated()

        # deploy the instance
        deployment.deploy(self.project_config, output, dry_run=dry_run)

    def stop(self, output: AbstractOutputWriter):
        # delete the stack and apply deletion policies
        self.instance_deployment.delete(output)

    def clean(self, output: AbstractOutputWriter):
        pass

    def sync(self, output: AbstractOutputWriter, dry_run=False):
        # create or get existing bucket for the project
        bucket_name = self.instance_deployment.bucket.get_or_create_bucket(output, self.project_config.tags, dry_run)

        # sync the project with S3 bucket
        output.write('Syncing the project with S3 bucket...')
        sync_project_with_s3(self.project_config.project_dir, bucket_name, self.instance_config.region,
                             self.project_config.sync_filters, dry_run=dry_run)

        if not dry_run:
            # sync S3 with the instance
            output.write('Syncing S3 bucket with the instance...')
            sync_instance_with_s3(self.project_config.sync_filters, self.get_ip_address(), self.ssh_port, self.ssh_user,
                                  self.ssh_key_path)

    def download(self, download_filters: list, output: AbstractOutputWriter, dry_run=False):
        # create or get existing bucket for the project
        bucket_name = self.instance_deployment.bucket.get_or_create_bucket(output, self.project_config.tags, dry_run)

        # sync files from the instance to a temporary S3 directory
        output.write('Uploading files from the instance to S3 bucket...')
        upload_from_instance_to_s3(download_filters, self.get_ip_address(), self.ssh_port, self.ssh_user, self.ssh_key_path,
                                   dry_run=dry_run)

        # sync the project with the S3 bucket
        output.write('Downloading files from S3 bucket to local...')
        download_from_s3_to_local(bucket_name, self.instance_config.name, self.project_config.project_dir,
                                  self.instance_config.region, download_filters, dry_run=dry_run)

    def get_status_text(self):
        instance = self.instance_deployment.get_instance()
        if not instance:
            raise InstanceNotRunningError(self.instance_config.name)

        table = [
            ('Instance State', instance.state),
            ('Instance Type', instance.instance_type),
            ('Availability Zone', instance.availability_zone),
        ]

        if instance.public_ip_address:
            table.append(('Public IP Address', instance.public_ip_address))

        table.append(('Launch Time', instance.launch_time.strftime('%Y-%m-%d %H:%M:%S')))

        if instance.lifecycle == 'spot':
            spot_price = instance.get_spot_price()
            table.append(('Purchasing Option', 'Spot Instance'))
            table.append(('Spot Instance Price', '$%.04f' % spot_price))
        else:
            table.append(('Purchasing Option', 'On-Demand Instance'))

        return render_table(table)

    def get_public_ip_address(self):
        """Returns a public IP address of the running instance."""
        instance = self.instance_deployment.get_instance()
        if not instance:
            raise InstanceNotRunningError(self.instance_config.name)

        return instance.public_ip_address

    @property
    def ssh_user(self):
        return 'ubuntu'

    @property
    def ssh_key_path(self):
        return self.instance_deployment.key_pair.key_path
