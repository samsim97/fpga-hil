import shutil
import click
from cli.common import VIVADO_PROJECT_DIR, VITIS_WORKSPACE_DIR


@click.command()
def clean():
    """Delete the generated Vivado project and Vitis workspace directories."""
    cleaned_anything = False

    if VIVADO_PROJECT_DIR.exists():
        shutil.rmtree(VIVADO_PROJECT_DIR)
        click.echo(f"Removed '{VIVADO_PROJECT_DIR}'.")
        cleaned_anything = True

    if VITIS_WORKSPACE_DIR.exists():
        shutil.rmtree(VITIS_WORKSPACE_DIR)
        click.echo(f"Removed '{VITIS_WORKSPACE_DIR}'.")
        cleaned_anything = True

    if not cleaned_anything:
        click.echo("Nothing to clean: no generated directories found.")
