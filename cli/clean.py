import shutil
import click
from cli.common import VIVADO_PROJECT_DIR


@click.command()
def clean():
    """Delete the Vivado project directory."""
    if not VIVADO_PROJECT_DIR.exists():
        click.echo(f"Nothing to clean: '{VIVADO_PROJECT_DIR}' does not exist.")
        return

    shutil.rmtree(VIVADO_PROJECT_DIR)
    click.echo(f"Removed '{VIVADO_PROJECT_DIR}'.")