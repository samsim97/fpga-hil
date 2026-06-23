from pathlib import Path
import click
from cli.common import run_vitis, VITIS_WORKSPACE_DIR, CONFIG_FILE

PY_SCRIPT = Path("vitis/scripts/create_apps.py")
PLATFORM_DIR = VITIS_WORKSPACE_DIR / "hil_platform"


@click.command()
def create_vitis_apps():
    """Create the hil_ctrl and hil_comm application components."""
    if not CONFIG_FILE.exists():
        click.echo("Error: config.json not found. Run 'init' first.")
        return

    if not PLATFORM_DIR.exists():
        click.echo(f"Error: platform not found at {PLATFORM_DIR}. Run 'vitis create-platform' first.")
        return

    click.echo(f"Creating Vitis applications from platform at {PLATFORM_DIR}...")
    return_code = run_vitis(PY_SCRIPT, str(VITIS_WORKSPACE_DIR.resolve()))
    if return_code != 0:
        click.echo("Error: Failed to create Vitis applications.")
    else:
        click.echo("Vitis applications 'hil_ctrl' and 'hil_comm' created successfully.")