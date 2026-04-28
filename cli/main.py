import click
from cli.init import init
from cli.create_project import create_project
from cli.add_hdl_files import add_hdl_files
from cli.add_constraints import add_constraints
from cli.add_cores import add_cores
from cli.clean import clean

@click.group()
def cli():
    pass

cli.add_command(init)
cli.add_command(create_project)
cli.add_command(add_hdl_files)
cli.add_command(add_constraints)
cli.add_command(add_cores)
cli.add_command(clean)

if __name__ == "__main__":
    cli()