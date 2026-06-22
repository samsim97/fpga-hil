import subprocess
import click
from cli.common import load_config, vitis_executable, VITIS_WORKSPACE_DIR


@click.command()
def open_vitis():
    """Open the Vitis workspace in the Unified IDE GUI."""
    config = load_config()
    if not config:
        click.echo("Error: config.json not found. Run 'init' first.")
        return

    if not VITIS_WORKSPACE_DIR.exists():
        click.echo(f"Error: Vitis workspace not found at {VITIS_WORKSPACE_DIR}. Run 'create-vitis-platform' first.")
        return

    # '-workspace' flag confirmed against an official Vitis platform-creation
    # tutorial (used as: vitis -workspace ./platform_repo &).
    cmd = [
        str(vitis_executable(config["vitis_bin_dir"])),
        "-w", str(VITIS_WORKSPACE_DIR.resolve()),
    ]

    subprocess.Popen(cmd)
    click.echo("Opening Vitis Unified IDE...")
