import json
import subprocess
import sys
from pathlib import Path
import click

CONFIG_FILE  = Path("config.json")
TCL_SCRIPT   = Path("vivado/scripts/create_project.tcl")
PROJECT_NAME = "hil"
VIVADO_DIR   = Path("vivado/hil")


def _vivado_executable(bin_dir: str) -> Path:
    exe = "vivado.bat" if sys.platform == "win32" else "vivado"
    return Path(bin_dir) / exe


@click.command()
def create_project():
    """Create the Vivado project."""
    if not CONFIG_FILE.exists():
        click.echo("Error: config.json not found. Run 'init' first.")
        return

    config = json.loads(CONFIG_FILE.read_text())
    vivado = _vivado_executable(config["vivado_bin_dir"])
    
    if not Path.exists(VIVADO_DIR):
        Path.mkdir(VIVADO_DIR, parents=True, exist_ok=True)

    cmd = [
        str(vivado),
        "-mode", "batch",
        "-source", str(TCL_SCRIPT.resolve()),
        "-tclargs", PROJECT_NAME, str(VIVADO_DIR.resolve()),
    ]

    result = subprocess.run(cmd, cwd=VIVADO_DIR)
    if result.returncode != 0:
        click.echo("Error: Vivado project creation failed.")
    else:
        click.echo(f"Project '{PROJECT_NAME}' created successfully.")