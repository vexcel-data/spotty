from spotty.commands.abstract_command import AbstractCommand
from spotty.commands.writers.abstract_output_writrer import AbstractOutputWriter
from argparse import Namespace
import uuid

class ForkIdCommand(AbstractCommand):
    name = 'fork-id'
    description = 'Generate fork id'

    def run(self, args: Namespace, output: AbstractOutputWriter):
        print(str(uuid.uuid4()).split('-')[-1])
