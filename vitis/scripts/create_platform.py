"""
Creates the 'hil_platform' Vitis platform component with three domains:
FSBL (boot), standalone CPU0 (real-time HIL logic), standalone+lwIP CPU1 (networking).

Run via: vitis -s create_platform.py <xsa_path> <workspace_dir>

VALIDATION STATUS - confirmed against a real Vitis 2025.2 session, not just docs:

CONFIRMED:
  - client.create_platform_component(name=, hw_design=, cpu=, os=, domain_name=)
    creates the platform with its first domain.
  - The FSBL boot domain is created AUTOMATICALLY as part of
    create_platform_component() itself, whenever the hw_design targets a device
    that needs one. Confirmed directly: a single create_platform_component() call
    for ps7_cortexa9_0/standalone produced both 'standalone_ps7_cortexa9_0' AND
    'zynq_fsbl' domains - visible in the build log ("Platform FSBL Boot domain
    added successfully") and in platform.list_domains() afterward, before any
    add_domain() call was made. No explicit step is needed for it here.
    (Consistent with this: add_domain()'s confirmed signature - cpu, os, name,
    display_name, sd_dir, support_app, generate_dtb, dt_overlay, architecture,
    compiler, hw_boot_bin - has no FSBL-specific parameter at all.)
  - platform.add_domain(cpu=, os=, name=, display_name=, support_app=) adds further
    domains. support_app=<app_name> pre-configures that domain's BSP with whatever
    library settings the named application template needs - confirmed via
    help(platform.add_domain). This is how lwIP gets attached to the CPU1 domain,
    rather than being a separate library-configuration step.
  - The platform must be built (platform.build()) AFTER all domains are created,
    not after each one.

Sources: official Xilinx Vitis-Tutorials repo (2025.2 branch), MicroZed Chronicles
blog, and a real interactive session run against this project's actual Vitis 2025.2
install (explore_domains.py).
"""
import sys
import vitis

xsa_path = sys.argv[1]
workspace_dir = sys.argv[2]

client = vitis.create_client()
client.set_workspace(path=workspace_dir)

# This single call also creates the FSBL boot domain automatically - confirmed,
# see header. No separate step needed for it.
platform = client.create_platform_component(
    name="hil_platform",
    hw_design=xsa_path,
    cpu="ps7_cortexa9_0",
    os="standalone",
    domain_name="standalone_ps7_cortexa9_0",
)

# CPU1: networking domain. No FreeRTOS - bare-metal standalone + lwIP per the
# settled architecture in .agent/skills/vitis-cli/SKILL.md.
# support_app="lwip_echo_server" configures this domain's BSP with the library
# settings the lwip_echo_server template needs (confirmed via help(add_domain)).
platform.add_domain(
    cpu="ps7_cortexa9_1",
    os="standalone",
    name="standalone_ps7_cortexa9_1",
    display_name="standalone_ps7_cortexa9_1",
    support_app="lwip_echo_server",
)

# Build after all domains exist.
platform.build()

client.close()
