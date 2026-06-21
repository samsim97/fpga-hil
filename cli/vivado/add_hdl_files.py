from pathlib import Path
import click
from cli.common import run_vivado, PROJECT_NAME, VIVADO_PROJECT_DIR, CONFIG_FILE

TCL_SCRIPT = Path("vivado/scripts/add_hdl_files.tcl")
HDL_DIR    = Path("design/hdl")


@click.command()
def add_hdl_files():
    """Add HDL files from design/hdl/ to the Vivado project."""
    if not CONFIG_FILE.exists():
        click.echo("Error: config.json not found. Run 'init' first.")
        return

    rc = run_vivado(TCL_SCRIPT, PROJECT_NAME, str(VIVADO_PROJECT_DIR.resolve()), str(HDL_DIR.resolve()))
    if rc != 0:
        click.echo("Error: Failed to add HDL files.")
    else:
        click.echo("HDL files added successfully.")