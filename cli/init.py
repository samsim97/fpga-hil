import json
from pathlib import Path
import click
from cli.common import CONFIG_FILE, vivado_executable, vitis_executable


@click.command()
@click.option("--force", is_flag=True, help="Re-configure even if config already exists.")
def init(force):
    """Initialize the project by configuring the Vivado and Vitis installation paths."""
    if CONFIG_FILE.exists() and not force:
        config = json.loads(CONFIG_FILE.read_text())
        click.echo(f"Already configured. Vivado bin directory: {config.get('vivado_bin_dir')}")
        click.echo(f"Already configured. Vitis bin directory: {config.get('vitis_bin_dir')}")
        click.echo("Use --force to reconfigure.")
        return

    while True:
        vivado_bin_dir = click.prompt("Enter path to Vivado bin directory").strip()
        vivado_bin_path = Path(vivado_bin_dir)
        executable = vivado_executable(vivado_bin_dir)
        if executable.exists():
            break
        click.echo(f"Error: '{executable}' not found. Please check the path.")

    while True:
        vitis_bin_dir = click.prompt("Enter path to Vitis bin directory").strip()
        vitis_bin_path = Path(vitis_bin_dir)
        executable = vitis_executable(vitis_bin_dir)
        if executable.exists():
            break
        click.echo(f"Error: '{executable}' not found. Please check the path.")

    config = {
        "vivado_bin_dir": str(vivado_bin_path),
        "vitis_bin_dir": str(vitis_bin_path),
    }
    CONFIG_FILE.write_text(json.dumps(config, indent=2))
    click.echo(f"Config saved to {CONFIG_FILE}")
