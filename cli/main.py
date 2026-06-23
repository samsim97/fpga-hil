import click
from cli.init import init
from cli.clean import clean
from cli.vivado.create_project import create_project
from cli.vivado.add_hdl_files import add_hdl_files
from cli.vivado.add_constraints import add_constraints
from cli.vivado.add_cores import add_cores
from cli.vivado.open_vivado import open_vivado
from cli.vivado.export_hardware import export_hardware
from cli.vitis.create_vitis_platform import create_vitis_platform
from cli.vitis.create_vitis_apps import create_vitis_apps
from cli.vitis.build_vitis import build_vitis
from cli.vitis.open_vitis import open_vitis


@click.group()
def cli():
    pass


@cli.group()
def vivado():
    """Commands for managing the Vivado project."""
    pass


@cli.group()
def vitis():
    """Commands for managing the Vitis workspace."""
    pass


cli.add_command(init)
cli.add_command(clean)

vivado.add_command(create_project)
vivado.add_command(add_hdl_files)
vivado.add_command(add_constraints)
vivado.add_command(add_cores)
vivado.add_command(export_hardware)
vivado.add_command(open_vivado, name="open")

vitis.add_command(create_vitis_platform, name="create-platform")
vitis.add_command(create_vitis_apps, name="create-apps")
vitis.add_command(build_vitis, name="build")
vitis.add_command(open_vitis, name="open")


if __name__ == "__main__":
    cli()