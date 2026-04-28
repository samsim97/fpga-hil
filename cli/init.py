import json
import sys
from pathlib import Path
import click

CONFIG_FILE = Path("config.json")


def _vivado_executable() -> str:
    return "vivado.bat" if sys.platform == "win32" else "vivado"


@click.command()
def init():
    """Initialize the project by configuring the Vivado installation path."""
    existing = {}
    if CONFIG_FILE.exists():
        existing = json.loads(CONFIG_FILE.read_text())
        current = existing.get("vivado_bin_dir", "")
        click.echo(f"Current Vivado bin directory: {current}")

    while True:
        bin_dir = click.prompt("Enter path to Vivado bin directory").strip()
        bin_path = Path(bin_dir)
        executable = bin_path / _vivado_executable()

        if executable.exists():
            break
        click.echo(f"Error: '{executable}' not found. Please check the path.")

    existing["vivado_bin_dir"] = str(bin_path)
    CONFIG_FILE.write_text(json.dumps(existing, indent=2))
    click.echo(f"Config saved to {CONFIG_FILE}")