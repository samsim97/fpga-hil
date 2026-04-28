import json
import subprocess
import sys
from pathlib import Path
import click

CONFIG_FILE        = Path("config.json")
PROJECT_NAME       = "hil"
VIVADO_PROJECT_DIR = Path("vivado/hil")


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    return json.loads(CONFIG_FILE.read_text())


def vivado_executable(bin_dir: str) -> Path:
    exe = "vivado.bat" if sys.platform == "win32" else "vivado"
    return Path(bin_dir) / exe


def run_vivado(tcl_script: Path, *tcl_args: str) -> int:
    config = load_config()
    if not config:
        return -1

    cmd = [
        str(vivado_executable(config["vivado_bin_dir"])),
        "-mode", "batch",
        "-source", str(tcl_script.resolve()),
        "-tclargs", *tcl_args,
    ]

    result = subprocess.run(cmd, cwd=VIVADO_PROJECT_DIR, capture_output=True, text=True)

    if result.returncode != 0:
        click.echo(result.stdout)

    return result.returncode