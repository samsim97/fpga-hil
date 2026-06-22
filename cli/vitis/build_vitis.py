from pathlib import Path
import click
from cli.common import run_vitis, VITIS_WORKSPACE_DIR, CONFIG_FILE

PY_SCRIPT = Path("vitis/scripts/build.py")


@click.command()
def build_vitis():
    """Build the Vitis platform and both applications."""
    if not CONFIG_FILE.exists():
        click.echo("Error: config.json not found. Run 'init' first.")
        return

    if not VITIS_WORKSPACE_DIR.exists():
        click.echo(f"Error: Vitis workspace not found at {VITIS_WORKSPACE_DIR}. Run 'vitis create-platform' first.")
        return

    rc = run_vitis(PY_SCRIPT, str(VITIS_WORKSPACE_DIR.resolve()))
    if rc != 0:
        click.echo("Error: Vitis build failed.")
    else:
        click.echo("Vitis platform and applications built successfully.")