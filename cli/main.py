import click
from cli.vivado.init import init
from cli.vivado.create_project import create_project
from cli.vivado.add_hdl_files import add_hdl_files
from cli.vivado.add_constraints import add_constraints
from cli.vivado.add_cores import add_cores
from cli.vivado.clean import clean
from cli.vivado.open_vivado import open_vivado
from cli.vivado.export_hardware import export_hardware
from cli.vitis.create_vitis_platform import create_vitis_platform
from cli.vitis.create_vitis_apps import create_vitis_apps
from cli.vitis.build_vitis import build_vitis
from cli.vitis.open_vitis import open_vitis

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
cli.add_command(export_hardware)
cli.add_command(create_vitis_platform)
cli.add_command(create_vitis_apps)
cli.add_command(build_vitis)
cli.add_command(open_vitis)

if __name__ == "__main__":
    cli()
