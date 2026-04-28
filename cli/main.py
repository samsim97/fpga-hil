import click
from cli.init import init

@click.group()
def cli():
    pass

cli.add_command(init)