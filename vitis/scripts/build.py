"""
Rebuilds the platform and both applications in an existing workspace.

Run via: vitis -s build.py <workspace_dir>

VALIDATION STATUS: client.get_component(name=) then .build() is confirmed against
the official Xilinx Vitis-Tutorials repo (2025.2 branch), which uses exactly this
pattern to rebuild a named component fetched from an existing workspace.
"""
import sys
import vitis

workspace_dir = sys.argv[1]

client = vitis.create_client()
client.set_workspace(path=workspace_dir)

platform = client.get_component(name="hil_platform")
platform.build()

hil_app = client.get_component(name="hil_app")
hil_app.build()

hil_net_app = client.get_component(name="hil_net_app")
hil_net_app.build()

client.close()
