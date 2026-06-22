import json
import subprocess
import sys
from pathlib import Path
import click

CONFIG_FILE         = Path("config.json")
PROJECT_NAME        = "hil"
VIVADO_PROJECT_DIR  = Path("vivado/hil")
VITIS_WORKSPACE_DIR = Path("vitis/hil")

# Output path of the .xsa produced by 'export-hardware'. This matches the path the
# user already referenced manually in their own Vitis platform project's
# vitis-comp.json ("C:/.../vivado/hil/hil/system_wrapper.xsa") - don't change this
# without also updating wherever Vitis-side scripts expect to find it.
XSA_PATH = VIVADO_PROJECT_DIR / PROJECT_NAME / "system_wrapper.xsa"


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    return json.loads(CONFIG_FILE.read_text())


def vivado_executable(bin_dir: str) -> Path:
    exe = "vivado.bat" if sys.platform == "win32" else "vivado"
    return Path(bin_dir) / exe


def vitis_executable(bin_dir: str) -> Path:
    exe = "vitis.bat" if sys.platform == "win32" else "vitis"
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


def run_vitis(py_script: Path, *script_args: str) -> int:
    """Run a Vitis Python automation script via 'vitis -s'.

    UNVERIFIED: passing extra plain arguments after the script path
    ('vitis -s script.py arg1 arg2', read inside the script via sys.argv[1:]) has
    not been confirmed against an actual Vitis install - it mirrors Vivado's
    '-tclargs' convention by analogy, not from a confirmed source. If this doesn't
    work, check 'vitis -s --help' on your machine, or hardcode paths inside each
    script instead of passing them as arguments.
    """
    config = load_config()
    if not config:
        return -1

    VITIS_WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)

    cmd = [
        str(vitis_executable(config["vitis_bin_dir"])),
        "-s", str(py_script.resolve()),
        *script_args,
    ]

    result = subprocess.run(cmd, cwd=VITIS_WORKSPACE_DIR, capture_output=True, text=True)

    if result.returncode != 0:
        # Echoing stderr too (unlike run_vivado, which only echoes stdout) since
        # uncaught Python exceptions in the Vitis script will land on stderr.
        click.echo(result.stdout)
        click.echo(result.stderr)

    return result.returncode
