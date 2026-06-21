import click
from cli.vivado.init import init
from cli.vivado.create_project import create_project
from cli.vivado.add_hdl_files import add_hdl_files
from cli.vivado.add_constraints import add_constraints
from cli.vivado.add_cores import add_cores
from cli.vivado.clean import clean
from cli.vivado.open_vivado import open_vivado

@click.group()
def cli():
    pass

cli.add_command(init)
cli.add_command(create_project)
cli.add_command(add_hdl_files)
cli.add_command(add_constraints)
cli.add_command(add_cores)
cli.add_command(clean)
cli.add_command(open_vivado)

if __name__ == "__main__":
    cli()