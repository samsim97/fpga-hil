from pathlib import Path
import click
from cli.common import run_vivado, PROJECT_NAME, VIVADO_PROJECT_DIR, CONFIG_FILE, XSA_PATH

TCL_SCRIPT = Path("vivado/scripts/export_hardware.tcl")


@click.command()
def export_hardware():
    """Run synthesis, implementation, and export the hardware platform (.xsa) for Vitis."""
    if not CONFIG_FILE.exists():
        click.echo("Error: config.json not found. Run 'init' first.")
        return

    project_file = VIVADO_PROJECT_DIR / PROJECT_NAME / f"{PROJECT_NAME}.xpr"
    if not project_file.exists():
        click.echo(f"Error: project file not found at {project_file}. Run 'create-project' first.")
        return

    rc = run_vivado(TCL_SCRIPT, PROJECT_NAME, str(VIVADO_PROJECT_DIR.resolve()), str(XSA_PATH.resolve()))
    if rc != 0:
        click.echo("Error: Failed to export hardware platform.")
    else:
        click.echo(f"Hardware platform exported to {XSA_PATH}.")
