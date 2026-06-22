"""
Creates the two application components against hil_platform:
  - hil_app:     CPU0, real-time HIL test logic, empty_application template
  - hil_net_app: CPU1, PS-to-host networking, bare-metal lwIP template

Run via: vitis -s create_apps.py <workspace_dir>

VALIDATION STATUS:

CONFIRMED:
  - client.create_app_component(name=, platform=, domain=, template=) then .build()
    (official Xilinx Vitis-Tutorials repo, 2025.2 branch)
  - "lwip_echo_server" is the correct template name for the bare-metal lwIP
    application - confirmed directly against the installed Vitis 2025.2
    sw_apps directory (<Vitis_install>/data/embeddedsw/lib/sw_apps/), where it
    sits alongside empty_application, hello_world, freertos_lwip_echo_server, etc.
  - The CPU1 domain in create_platform.py is created with
    support_app="lwip_echo_server", so its BSP should already carry the library
    settings this template needs.

STILL TO VERIFY (lower stakes, not blocking):
  - The expected platform .xpfm path below
    (<workspace>/hil_platform/export/hil_platform/hil_platform.xpfm) is inferred
    from the reference repos' directory layout. The interactive session that
    confirmed the FSBL/lwIP behavior didn't exercise create_app_component, so this
    path hasn't been directly confirmed - worth a quick check the first time this
    script actually runs (e.g. after create_platform.py, look at what actually
    landed under <workspace>/hil_platform/export/).
"""
import sys
from pathlib import Path
import vitis

workspace_dir = sys.argv[1]
platform_xpfm = str(Path(workspace_dir) / "hil_platform" / "export" / "hil_platform" / "hil_platform.xpfm")

client = vitis.create_client()
client.set_workspace(path=workspace_dir)

hil_app = client.create_app_component(
    name="hil_app",
    platform=platform_xpfm,
    domain="standalone_ps7_cortexa9_0",
    template="empty_application",
)
hil_app.build()

hil_net_app = client.create_app_component(
    name="hil_net_app",
    platform=platform_xpfm,
    domain="standalone_ps7_cortexa9_1",
    template="lwip_echo_server",
)
hil_net_app.build()

client.close()
