---
name: vitis-cli
description: Architecture decisions and conventions for the Vitis platform/application CLI tooling in fpga-hil. Consult this skill before writing, editing, or extending any `hil` CLI command that touches Vitis (platform creation, application creation, building, opening the IDE) or the Vivado-side hardware export step it depends on. Also consult before adding scripts under vitis/scripts/, editing cli/common.py for Vitis support, or changing config.json's vitis_bin_dir handling. Do not assume anything not written here — if a decision isn't documented in this file, treat it as unsettled and ask before proceeding.
---

# Vitis CLI tooling

## Purpose

This extends the existing `hil` CLI (which manages the Vivado project) with equivalent
commands for the Vitis side: turning the Vivado hardware design into a bootable
platform and software applications for the Zybo Z7-20's dual Cortex-A9.

**Repo placement (settled):** this lives in the same repo as the Vivado tooling -
`vitis/` sits alongside `vivado/` as a top-level folder, not in a separate repo. See
`doc/repository-architecture.md` for the full reasoning (short version: Vitis
platform creation has a hard dependency on the `.xsa` produced by the Vivado side,
and splitting repos would mean committing that generated artifact, scripting a
cross-repo handoff, or some other complexity not proportionate to the project's
current scale). This is reversible later if a concrete need for separation shows up.

Read `cli/common.py`, `cli/create_project.py`, and `vivado/scripts/create_project.tcl`
first — every Vitis command should follow the same shape as the Vivado equivalent.

## Settled architecture

**Scripting mechanism: Python, via the Vitis Unified IDE API (`vitis -s script.py` /
`vitis.create_client()`), not Tcl/XSCT.** As of Vitis 2025.1, XSCT is deprecated by
AMD in favor of this Python API, so this isn't a riskier choice than Tcl — it's the
supported one. Shape of the API:

```python
import vitis
client = vitis.create_client()
client.set_workspace(path=workspace_dir)
platform_comp = client.create_platform_component(
    name="hil_platform", hw_design=xsa_path,
    cpu="ps7_cortexa9_0", os="standalone", domain_name="standalone_ps7_cortexa9_0",
)
platform_comp.build()
app_comp = client.create_app_component(
    name="hil_app", platform=platform_xpfm_path,
    domain="standalone_ps7_cortexa9_0", template="empty_application",
)
app_comp.build()
client.close()
```

**Version control: nothing generated gets committed.** Mirrors `vivado/hil/` being
fully gitignored — only hand-written application source and the automation scripts
that regenerate everything else are tracked. Vitis-generated platforms carry a huge
auto-generated BSP tree per domain (vendor drivers, lwIP, prebuilt `.a` libs,
CMake/Ninja build dirs) plus `vitis-comp.json` / `app.yaml` files containing
machine-specific absolute paths — none of that is safe or useful to commit.

**Scope (current): platform + application creation/build only.** No JTAG
download/debug-launch automation yet. This mirrors the current Vivado CLI
(`create-project`, `add-hdl-files`, `open-vivado`) rather than building a full
deploy pipeline.

**Naming: fixed, mirroring `PROJECT_NAME = "hil"`** (no CLI-supplied names, same as
the Vivado side):
- Platform component: `hil_platform`
- App component, CPU0 (real-time HIL logic): `hil_app`
- App component, CPU1 (networking): `hil_net_app`
- Domain names follow Vitis's own `<os>_<cpu_instance>` convention rather than a
  custom scheme: `standalone_ps7_cortexa9_0`, `standalone_ps7_cortexa9_1`
- FSBL boot domain: keep Vitis's default name/template as-is (it's boilerplate,
  not something to customize)

## Platform domain layout

Three domains, intentionally **not** Vitis Unified IDE's default pairing (which is
FSBL + standalone CPU0 + FreeRTOS/lwIP CPU1):

| Domain | CPU | OS | Purpose |
|---|---|---|---|
| FSBL (boot) | `ps7_cortexa9_0` | standalone | Mandatory — Vitis requires this for any bootable platform |
| `standalone_ps7_cortexa9_0` | `ps7_cortexa9_0` | standalone | Real-time HIL test logic (stimulus/measurement, including physical simulation computation for sensor emulation). Kept isolated from networking so timing isn't affected by network jitter. |
| `standalone_ps7_cortexa9_1` | `ps7_cortexa9_1` | standalone + lwIP, **no FreeRTOS** | PS-to-host networking (report results / receive commands). Bare-metal lwIP (Xilinx's "lwIP echo server" bare-metal template) is sufficient — no RTOS needed for this. |

Why split across two cores at all: HIL test routines have real timing requirements,
and the user deliberately chose to isolate them from lwIP's TCP/IP processing rather
than share one core. Why *not* FreeRTOS: bare-metal lwIP is simpler and sufficient
for this use case — no task scheduling or sockets API is needed.

**Deferred, not blocking CLI work:** how `hil_app` (CPU0) and `hil_net_app` (CPU1)
communicate with each other (shared DDR region, mailbox/IPI, OpenAMP, etc.) is an
application-code design question, not a CLI-tooling question. Don't make assumptions
about this when implementing the CLI commands — it doesn't affect how platform/app
creation is scripted.

## The Vivado-side gap: hardware export

Nothing in the current Vivado CLI runs synthesis, implementation, or
`write_hw_platform` — but the Vitis platform needs the resulting `.xsa`. A new
Vivado CLI command is needed:

- **Command name:** `export-hardware`
- **New file:** `cli/export_hardware.py` (follow the shape of `cli/add_hdl_files.py`)
- **New TCL script:** `vivado/scripts/export_hardware.tcl` (follow the shape of
  `vivado/scripts/add_hdl_files.tcl`), running roughly:
  `synth_design → opt_design → place_design → route_design → write_bitstream →
  write_hw_platform -fixed -include_bit -force`
- **Output path:** `vivado/hil/hil/system_wrapper.xsa` — this matches the path the
  user already referenced manually in their own platform project
  (`vitis-comp.json`'s `"xsa"` field), so don't invent a different convention.
- Confirm before implementing: whether any non-default synthesis/implementation
  options matter (out-of-context synthesis, specific strategies, etc.) — assume
  standard default flow unless told otherwise.

## Proposed repo layout

```
vitis/
├── scripts/                  # Python automation, mirrors vivado/scripts/*.tcl
│   ├── create_platform.py
│   ├── create_apps.py
│   └── build.py
└── hil/                      # Generated workspace — gitignored entirely, like vivado/hil/
```

`config.json` gains a second key alongside `vivado_bin_dir`:

```json
{
  "vivado_bin_dir": "...",
  "vitis_bin_dir": "..."
}
```

Confirm before implementing: whether Vitis lives in the same install root as Vivado
(could maybe be derived automatically) or genuinely needs its own prompt in `init`.
Default assumption: prompt for it separately, same pattern as `init.py`'s existing
`bin_dir` prompt/validation loop.

## Planned CLI commands

| Command | File | Mirrors | Notes |
|---|---|---|---|
| `export-hardware` | `cli/export_hardware.py` | `add_hdl_files.py` | Vivado-side; produces the `.xsa` |
| `create-vitis-platform` | `cli/create_vitis_platform.py` | `create_project.py` | Creates `hil_platform` with the three domains above |
| `create-vitis-apps` | `cli/create_vitis_apps.py` | `add_hdl_files.py` | Creates `hil_app` + `hil_net_app` against the platform |
| `build-vitis` | `cli/build_vitis.py` | — (new) | Builds platform + both apps |
| `open-vitis` | `cli/open_vitis.py` | `open_vivado.py` | Opens Vitis Unified IDE GUI on the workspace |

`clean` has been extended to also remove `vitis/hil/` alongside `vivado/hil/`
(implemented — see `cli/clean.py`), rather than adding a separate clean command.

## Conventions to match from the existing Vivado CLI

- `cli/common.py`-style helpers: `vitis_executable(bin_dir)` and `run_vitis()`
  (both implemented), analogous to `run_vivado()`, calling `vitis -s <script.py>`
  instead of `vivado -mode batch -source <script.tcl>`.
- Error message style: `"Error: config.json not found. Run 'init' first."` /
  `"Error: project file not found at {path}. Run 'create-project' first."` — every
  new command should fail this way, telling the user exactly which prior command to
  run.
- Use `Path` objects and `.resolve()` for all filesystem paths, never hardcode
  separators — this is what keeps the existing CLI cross-platform.
- No new dependencies beyond what's already in `pyproject.toml`. Confirmed: every
  new `cli/*.py` file only needs `click` + stdlib (`pathlib`, `subprocess`, `sys`,
  `json`), already covered by the existing `bootstrap.bat`/`bootstrap.sh`. The
  `vitis/scripts/*.py` files run under Vitis's own bundled Python interpreter (via
  `vitis -s`), not the repo's `.venv` at all — they have no pip-installable
  dependencies to declare either. No new/separate bootstrap scripts are needed.

## Open items (confirm before/while implementing, don't assume)

- **How the FSBL boot domain gets created via the Python API.** Not found in any
  confirmed source — might be automatic when the first standalone domain is added
  for a Zynq-7000 XSA, or might need an explicit `add_domain()` call with
  parameters beyond `cpu`/`os`/`name`/`display_name`. Verify interactively
  (`vitis -i`, then `help(platform.add_domain)`) before trusting platform creation
  to produce a bootable image.
- **The exact app template string for bare-metal lwIP** (used for `hil_net_app`).
  `"lwip_echo_server"` is an educated guess, not confirmed — check available
  templates interactively before relying on it.
- Exact Vitis workspace internal layout (where `client.set_workspace()` should point
  relative to `vitis/hil/`, and whether platform/app subfolders need specific
  relative-path handling) — verify empirically when writing `create_platform.py`,
  don't assume it matches the manually-created reference repos exactly.
- Whether `export-hardware` needs any non-default Vivado synthesis/implementation
  options.
- Whether `vitis_bin_dir` should be derived from `vivado_bin_dir` or configured
  separately.
- Inter-core (CPU0 ↔ CPU1) communication mechanism — explicitly out of scope for the
  CLI itself, but will need its own decision before `hil_app`/`hil_net_app` source
  code is written.
