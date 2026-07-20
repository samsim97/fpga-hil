"""
Creates the two application components against hil_platform:
  - hil_comm: PS-to-host networking, bare-metal lwIP template (CPU0)
  - hil_ctrl: real-time HIL control logic, empty_application template (CPU1)

Run via: vitis -s create_apps.py <workspace_dir>

VALIDATION STATUS:

CONFIRMED:
  - client.create_app_component(name=, platform=, domain=, template=) then .build()
    (official Xilinx Vitis-Tutorials repo, 2025.2 branch)
  - "lwip_echo_server" is the correct template name for the bare-metal lwIP
    application - confirmed directly against the installed Vitis 2025.2
    sw_apps directory (<Vitis_install>/data/embeddedsw/lib/sw_apps/), where it
    sits alongside empty_application, hello_world, freertos_lwip_echo_server, etc.
  - The CPU0 domain in create_platform.py is created with
    template="lwip_echo_server", so its BSP should already carry the library
    settings this template needs.
  - _createHostComponent() calls os.path.abspath() on the platform argument, so
    passing a bare name like "hil_platform" resolves to <CWD>/hil_platform, NOT
    a platform-repo lookup. Must pass the absolute path to the .xpfm file.
  - client.add_platform_repos(platform=<path>) must be called before
    create_app_component or the server returns "does not exist in the repository".
    The path is the directory that *contains* the platform directory
    (i.e. export/, which contains hil_platform/).
  - 'vitis -s' intercepts sys.exit() via 'except BaseException' and returns 0.
    Use os._exit(1) to force a non-zero exit code on failure.
"""
import os
import shutil
import sys
from pathlib import Path
import vitis

workspace_dir = sys.argv[1]
platform_repo  = str(Path(workspace_dir) / "hil_platform" / "export")
platform_xpfm  = str(Path(workspace_dir) / "hil_platform" / "export" / "hil_platform" / "hil_platform.xpfm")
fw_dir = Path(workspace_dir).parent.parent / "fw"


def import_fw_sources(component_name: str) -> None:
    """Copy fw/<component_name>/ into the component's src/ directory, preserving structure."""
    src_dir = fw_dir / component_name
    dest_dir = Path(workspace_dir) / component_name / "src"
    files = [f for f in src_dir.rglob("*") if f.is_file() and f.name != ".gitkeep"]
    if not files:
        return
    shutil.copytree(src_dir, dest_dir, ignore=shutil.ignore_patterns(".gitkeep"), dirs_exist_ok=True)
    print(f"Imported {len(files)} source file(s) into {component_name}/src/")

client = vitis.create_client()

try:
    client.set_workspace(path=workspace_dir)
    client.add_platform_repos(platform=platform_repo)

    hil_comm = client.create_app_component(
        name="hil_comm",
        platform=platform_xpfm,
        domain="standalone_ps7_cortexa9_0",
        template="lwip_echo_server",
    )
    import_fw_sources("hil_comm")
    hil_comm.build()

    hil_ctrl = client.create_app_component(
        name="hil_ctrl",
        platform=platform_xpfm,
        domain="standalone_ps7_cortexa9_1",
        template="empty_application",
    )
    import_fw_sources("hil_ctrl")
    hil_ctrl.build()
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.stderr.flush()
    os._exit(1)

client.close()
