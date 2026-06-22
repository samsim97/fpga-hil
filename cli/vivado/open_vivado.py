import subprocess
from pathlib import Path
import click
from cli.common import load_config, vivado_executable, VIVADO_PROJECT_DIR, PROJECT_NAME


@click.command()
def open_vivado():
    """Open the Vivado project in the GUI."""
    config = load_config()
    if not config:
        click.echo("Error: config.json not found. Run 'init' first.")
        return

    project_file = VIVADO_PROJECT_DIR / "hil" / f"{PROJECT_NAME}.xpr"
    if not project_file.exists():
        click.echo(f"Error: project file not found at {project_file}. Run 'vivado create-project' first.")
        return

    cmd = [
        str(vivado_executable(config["vivado_bin_dir"])),
        "-mode", "gui",
        str(project_file.resolve()),
    ]

    subprocess.Popen(cmd, cwd=VIVADO_PROJECT_DIR)
    click.echo(f"Opening Vivado project '{PROJECT_NAME}'...")