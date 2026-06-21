from pathlib import Path
import click
from cli.common import run_vivado, PROJECT_NAME, VIVADO_PROJECT_DIR, CONFIG_FILE

TCL_SCRIPT      = Path("vivado/scripts/add_constraints.tcl")
CONSTRAINTS_DIR = Path("design/constraints")


@click.command()
def add_constraints():
    """Add constraint files from design/constraints/ to the Vivado project."""
    if not CONFIG_FILE.exists():
        click.echo("Error: config.json not found. Run 'init' first.")
        return

    rc = run_vivado(TCL_SCRIPT, PROJECT_NAME, str(VIVADO_PROJECT_DIR.resolve()), str(CONSTRAINTS_DIR.resolve()))
    if rc != 0:
        click.echo("Error: Failed to add constraint files.")
    else:
        click.echo("Constraint files added successfully.")