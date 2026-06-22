from pathlib import Path
import click
from cli.common import run_vitis, VITIS_WORKSPACE_DIR, CONFIG_FILE

PY_SCRIPT = Path("vitis/scripts/create_apps.py")

# Expected location of the built platform component inside the workspace.
# UNVERIFIED: inferred from Vitis's typical "component name = subdirectory name"
# workspace layout (matches the structure seen in the manually-created reference
# repos), not from a directly confirmed source. Check after the first real run.
PLATFORM_DIR = VITIS_WORKSPACE_DIR / "hil_platform"


@click.command()
def create_vitis_apps():
    """Create the hil_app (CPU0) and hil_net_app (CPU1) application components."""
    if not CONFIG_FILE.exists():
        click.echo("Error: config.json not found. Run 'init' first.")
        return

    if not PLATFORM_DIR.exists():
        click.echo(f"Error: platform not found at {PLATFORM_DIR}. Run 'create-vitis-platform' first.")
        return

    rc = run_vitis(PY_SCRIPT, str(VITIS_WORKSPACE_DIR.resolve()))
    if rc != 0:
        click.echo("Error: Failed to create Vitis applications.")
    else:
        click.echo("Vitis applications 'hil_app' and 'hil_net_app' created successfully.")
