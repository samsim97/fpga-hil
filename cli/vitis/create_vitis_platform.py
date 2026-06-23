from pathlib import Path
import click
from cli.common import run_vitis, XSA_PATH, VITIS_WORKSPACE_DIR, CONFIG_FILE

PY_SCRIPT = Path("vitis/scripts/create_platform.py")


@click.command()
def create_vitis_platform():
    """Create the hil_platform Vitis platform component from the exported hardware."""
    if not CONFIG_FILE.exists():
        click.echo("Error: config.json not found. Run 'init' first.")
        return

    if not XSA_PATH.exists():
        click.echo(f"Error: hardware platform not found at {XSA_PATH}. Run 'vivado export-hardware' first.")
        return

    click.echo(f"Creating Vitis platform from {XSA_PATH}...")
    return_code = run_vitis(PY_SCRIPT, str(XSA_PATH.resolve()), str(VITIS_WORKSPACE_DIR.resolve()))
    if return_code != 0:
        click.echo("Error: Failed to create Vitis platform.")
    else:
        click.echo("Vitis platform 'hil_platform' created successfully.")