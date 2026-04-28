import json
import sys
from pathlib import Path
import click

CONFIG_FILE = Path("config.json")


def _vivado_executable() -> str:
    return "vivado.bat" if sys.platform == "win32" else "vivado"


@click.command()
@click.option("--force", is_flag=True, help="Re-configure even if config already exists.")
def init(force):
    """Initialize the project by configuring the Vivado installation path."""
    if CONFIG_FILE.exists() and not force:
        config = json.loads(CONFIG_FILE.read_text())
        click.echo(f"Already configured. Vivado bin directory: {config.get('vivado_bin_dir')}")
        click.echo("Use --force to reconfigure.")
        return

    while True:
        bin_dir = click.prompt("Enter path to Vivado bin directory").strip()
        bin_path = Path(bin_dir)
        executable = bin_path / _vivado_executable()

        if executable.exists():
            break
        click.echo(f"Error: '{executable}' not found. Please check the path.")

    config = {"vivado_bin_dir": str(bin_path)}
    CONFIG_FILE.write_text(json.dumps(config, indent=2))
    click.echo(f"Config saved to {CONFIG_FILE}")