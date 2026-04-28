import click
from cli.init import init
from cli.create_project import create_project

@click.group()
def cli():
    pass

cli.add_command(init)
cli.add_command(create_project)

if __name__ == "__main__":
    cli()