"""
Creates the 'hil_platform' Vitis platform component with three domains:
FSBL (boot), standalone CPU0 (real-time HIL logic), standalone+lwIP CPU1 (networking).

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
"""
import os
import sys
import vitis

xsa_path = sys.argv[1]
workspace_dir = sys.argv[2]

client = vitis.create_client()

try:
    client.set_workspace(path=workspace_dir)

    platform = client.create_platform_component(
        name="hil_platform",
        hw_design=xsa_path,
        cpu="ps7_cortexa9_0",
        os="standalone",
        domain_name="standalone_ps7_cortexa9_0",
    )

    platform.add_domain(
        cpu="ps7_cortexa9_1",
        os="standalone",
        name="standalone_ps7_cortexa9_1",
        display_name="standalone_ps7_cortexa9_1",
        support_app="lwip_echo_server",
    )

    platform.build()
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.stderr.flush()
    os._exit(1)

client.close()
