from pathlib import Path
import click
from cli.common import run_vivado, PROJECT_NAME, VIVADO_PROJECT_DIR, CONFIG_FILE

CREATE_PROJECT_TCL_SCRIPT = Path("vivado/scripts/create_project.tcl")
ADD_AND_CONFIGURE_MPU_TCL_SCRIPT = Path("vivado/scripts/add_and_configure_mpu.tcl")


@click.command()
def create_project():
    """Create the Vivado project and configure the MPU."""
    if not CONFIG_FILE.exists():
        click.echo("Error: config.json not found. Run 'init' first.")
        return

    VIVADO_PROJECT_DIR.mkdir(parents=True, exist_ok=True)
    return_code = run_vivado(CREATE_PROJECT_TCL_SCRIPT, PROJECT_NAME, str(VIVADO_PROJECT_DIR.resolve()))
    if return_code != 0:
        click.echo("Error: Vivado project creation failed.")
        return
    
    click.echo(f"Project '{PROJECT_NAME}' created successfully. Adding and configuring MPU...")
    return_code = run_vivado(ADD_AND_CONFIGURE_MPU_TCL_SCRIPT, PROJECT_NAME, str(VIVADO_PROJECT_DIR.resolve()))
    if return_code != 0:
        click.echo("Error: Failed to add and configure MPU.")
    else:
        click.echo(f"MPU added and configured successfully in project '{PROJECT_NAME}'.")
