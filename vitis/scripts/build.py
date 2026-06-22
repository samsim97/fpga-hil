"""
Rebuilds the platform and both applications in an existing workspace.

Run via: vitis -s build.py <workspace_dir>

VALIDATION STATUS: client.get_component(name=) then .build() is confirmed against
the official Xilinx Vitis-Tutorials repo (2025.2 branch), which uses exactly this
pattern to rebuild a named component fetched from an existing workspace.
"""
import os
import sys
import vitis

workspace_dir = sys.argv[1]

client = vitis.create_client()

try:
    client.set_workspace(path=workspace_dir)

    platform = client.get_component(name="hil_platform")
    platform.build()

    hil_ctrl = client.get_component(name="hil_ctrl")
    hil_ctrl.build()

    hil_comm = client.get_component(name="hil_comm")
    hil_comm.build()
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.stderr.flush()
    os._exit(1)

client.close()
