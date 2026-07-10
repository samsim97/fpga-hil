# Repository Review

## Overview

Two scopes are covered below: **Architecture** and **Code Logic**.
Each finding is classified as **CRITICAL** (broken or silently wrong), **WARNING** (confusing, inconsistent, or fragile), or **INFO** (minor cleanup, cosmetic, open question).

The Verilog files in `design/hdl/` are test artifacts used to validate the Vivado project generation flow, not part of the production design. They are excluded from this review.

---

## 1. Architecture

### CRITICAL

#### C-A1 — `create_project.py` is not using `common.py`

`cli/vivado/create_project.py` duplicates `CONFIG_FILE`, `PROJECT_NAME`, `VIVADO_DIR`, and a local `_vivado_executable()` function — all of which already exist in `cli/common.py`. Every other command in `cli/vivado/` and `cli/vitis/` imports from `common.py`. `create_project.py` was either written before `common.py` existed or was never migrated. If a constant is changed in `common.py`, `create_project.py` silently diverges.

Additionally, `create_project.py` runs its own `subprocess.run()` without `capture_output=True`, so Vivado raw output streams to the terminal instead of being routed through the consistent error-display logic in `run_vivado()`.

**Fix:** rewrite `create_project.py` to import from `common.py` and call `run_vivado()`, exactly like `add_hdl_files.py`.

#### C-A2 — `init.py` duplicates constants and lives in the wrong package

`cli/vivado/init.py` declares its own `CONFIG_FILE`, `_vivado_executable()`, and `_vitis_executable()`, all of which are already in `common.py`. It also lives in `cli/vivado/` but is registered as a top-level command (`cli.add_command(init)`), not under the `vivado` group. `init` configures both Vivado *and* Vitis, so placing it under `cli/vivado/` is misleading.

**Fix:** move `init.py` to `cli/init.py`, remove the duplicated constants, and import from `common.py`.

#### C-A3 — `init.py` and `clean.py` belong in `cli/`, not `cli/vivado/`

`init` initializes paths for both Vivado and Vitis. `clean` removes both `VIVADO_PROJECT_DIR` and `VITIS_WORKSPACE_DIR`. Both are cross-cutting commands, yet they sit in `cli/vivado/`. A contributor reading the code would reasonably expect all Vivado-specific files in that package.

**Fix:** move both to `cli/` and update their imports in `main.py`.

---

### WARNING

#### W-A1 — `run_vivado()` fails silently on missing config

When `config.json` is absent, `run_vivado()` returns `-1` with no output. Every caller that checks `CONFIG_FILE.exists()` before calling `run_vivado()` is protected, but the silent `-1` return is a trap for any future caller that skips the pre-check. The callers' own "Error: config.json not found" messages carry all the useful text; `run_vivado()` swallowing the failure silently is just confusing.

**Fix:** have `run_vivado()` emit an error and return early, or remove the config check from it entirely and trust callers to guard (which they already do).

#### W-A2 — `run_vivado()` only prints stdout on failure; `run_vitis()` always prints both

These two runner functions behave differently: `run_vivado()` shows output only on non-zero exit code; `run_vitis()` always prints stdout and stderr. The `run_vitis()` comment explains why ("failures sometimes come back with return_code=0"). Vivado batch-mode can also produce useful diagnostics on success. The inconsistency has no strong justification.

#### W-A3 — `open_vivado.py` hardcodes `"hil"` in the project file path

```python
project_file = VIVADO_PROJECT_DIR / "hil" / f"{PROJECT_NAME}.xpr"
```

Since `PROJECT_NAME = "hil"`, this resolves to `vivado/hil/hil/hil.xpr` — correct by coincidence. `export_hardware.py` uses `VIVADO_PROJECT_DIR / PROJECT_NAME / f"{PROJECT_NAME}.xpr"`, which is the right pattern. If `PROJECT_NAME` ever changes, `open_vivado.py` breaks while `export_hardware.py` stays correct.

#### W-A4 — `fw_dir` path in `vitis/scripts/create_apps.py` encodes an implicit repo-root assumption

```python
fw_dir = Path(workspace_dir).parent.parent / "fw"
```

This navigates two levels up from `vitis/hil/` to the repo root, then into `fw/`. It works only when the workspace is exactly at `<repo_root>/vitis/hil/`. If the workspace ever moves, this silently resolves to the wrong directory with no error until the copy step produces no files.

**Fix:** pass `fw_dir` as a CLI argument from `create_vitis_apps.py`, the same way `xsa_path` and `workspace_dir` are already passed to other scripts.

#### W-A5 — Lock-file deletion in `run_vitis()` is unsafe when the Vitis GUI is open

The comment says: *"Deleting [the lock] pre-flight is safe because we verified no Vitis process is running (run_vitis() is the only entry point that opens the workspace)."* But `open_vitis` (which launches the GUI) also opens the same workspace. If the user has the GUI open and then runs a CLI command, the lock is stolen from the live GUI session.

**Fix:** before deleting the lock, check whether any `vitis` process is running and abort if one is found (or at least warn).

#### W-A6 — No validation on `config.json` keys

Config values are accessed with `config["vivado_bin_dir"]` and `config["vitis_bin_dir"]`. Any user who configured the project before Vitis support was added will have a `config.json` with only `vivado_bin_dir`. Running any Vitis command will raise a raw `KeyError` instead of a helpful prompt.

**Fix:** either check for the key explicitly with a clear error message, or re-run the init prompt for the missing key.

#### W-A7 — `create_project.tcl` has no Linux board repository path handling

```tcl
if {$tcl_platform(os) eq "Windows NT"} {
    set board_repo_path "$env(APPDATA)/Xilinx/..."
    set_param board.repoPaths $board_repo_path
}
```

There is no `else` branch. On Linux, the board repository path is not set, which may or may not matter depending on where the user installed the board files. The README covers this setup for Windows only. If the project is ever used on Linux, this will be a silent failure point.

---

### INFO

#### I-A1 — `hil.egg-info/` is generated and gitignored but exists on disk

`hil.egg-info/` is generated by `pip install -e .` (run by bootstrap) and correctly gitignored. No action needed — it is just worth knowing it's there and not tracked.

#### I-A2 — No `config.json.example` for new contributors

`config.json` is gitignored (correct — it contains machine-specific paths). But a new contributor who wants to understand the format without running `hil init` has no reference. An example or a schema comment in the README would help.

---

## 2. Code Logic

### CRITICAL

#### C-L1 — `Path.exists()` and `Path.mkdir()` called as class methods in `create_project.py`

```python
if not Path.exists(VIVADO_DIR):
    Path.mkdir(VIVADO_DIR, parents=True, exist_ok=True)
```

This is calling `Path.exists` as an unbound class method with an instance argument. It works in Python because Path is a descriptor, but it is not idiomatic and is a static-analysis warning. The correct form is:

```python
VIVADO_DIR.mkdir(parents=True, exist_ok=True)
```

(The `if not exists` check is also redundant because `mkdir(exist_ok=True)` already handles the case.)

---

### WARNING

#### W-L1 — `create_project.py` subprocess has no output capture

```python
result = subprocess.run(cmd, cwd=VIVADO_DIR)
```

All other commands route through `run_vivado()` which uses `capture_output=True, text=True`. The inconsistency means `create_project` spews raw Vivado output to the terminal while other commands show nothing (or only on failure). This may be intentional (the project-creation step is long and real-time feedback is useful), but if so it should be explicit, not accidental.

#### W-L2 — `create_project.tcl` contains dead commented-out code

Lines 1–7 are identical to lines 17–25 but commented out. These are development leftovers.

```tcl
# set project_name [lindex $argv 0]   ← dead
# set project_dir  [lindex $argv 1]   ← dead
# ...
set project_name [lindex $argv 0]     ← live
set project_dir  [lindex $argv 1]     ← live
```

#### W-L3 — `os._exit(1)` called after `client.close()` in `create_platform.py` on the happy path

The Vitis scripts correctly use `os._exit(1)` in the `except` block (per the documented behavior that `vitis -s` intercepts `sys.exit()`). However, the happy path calls `client.close()` after the `try` block. The SKILL.md warns: *"Do NOT call `client.close()` before `os._exit(1)`"* — this is respected on the error path. But to be consistent and to match the documented pattern, the structure is correct as-is. Just noting that the relationship between `client.close()` and `os._exit(1)` is a subtle invariant that must not be changed without understanding the shutdown hook.

#### W-L4 — `add_constraints.tcl` does not call `update_compile_order`

`add_hdl_files.tcl` calls `update_compile_order -fileset sources_1` after adding files. `add_constraints.tcl` does not call any equivalent after adding constraint files. This is probably correct (constraint files don't affect compile order), but it should be confirmed: some constraint types (e.g., XDC with `set_property` on sources) can affect elaboration.

#### W-L5 — `build_vitis.py` checks for workspace existence, not for the platform

```python
if not VITIS_WORKSPACE_DIR.exists():
    click.echo(f"Error: Vitis workspace not found at {VITIS_WORKSPACE_DIR}. Run 'vitis create-platform' first.")
```

A workspace directory can exist without the platform having been built (e.g., if `create-platform` failed mid-run). The check passes but `build.py` then fails on `client.get_component(name="hil_platform")`. A better guard would check for the platform export: `VITIS_WORKSPACE_DIR / "hil_platform" / "export"`.

---

### INFO

#### I-L1 — `add_cores.py` is a stub

```python
click.echo("Not implemented yet.")
```

This is fine for now, but the command appears in `hil vivado --help` and gives no indication of when it will be implemented or what it will do.

#### I-L2 — Long VALIDATION STATUS docstrings in `vitis/scripts/`

The `create_platform.py` and `create_apps.py` scripts have large module-level docstrings documenting API validation. The content is valuable (it records non-obvious behavior like FSBL being automatic, `os._exit()` being required, etc.), but the format mixes API reference with design rationale. Consider keeping only the non-obvious behavioral notes (FSBL, lock file, `os._exit`) and trimming the rest.

---

## Summary Table

| ID | Scope | Severity | Short Description |
|----|-------|----------|-------------------|
| C-A1 | Architecture | CRITICAL | `create_project.py` not using `common.py` |
| C-A2 | Architecture | CRITICAL | `init.py` duplicates constants, wrong package |
| C-A3 | Architecture | CRITICAL | `init` and `clean` belong in `cli/`, not `cli/vivado/` |
| W-A1 | Architecture | WARNING | `run_vivado()` silent failure on missing config |
| W-A2 | Architecture | WARNING | `run_vivado` / `run_vitis` output handling inconsistency |
| W-A3 | Architecture | WARNING | `open_vivado.py` hardcodes literal `"hil"` in path |
| W-A4 | Architecture | WARNING | `fw_dir` implicit repo-root assumption in `create_apps.py` |
| W-A5 | Architecture | WARNING | Lock deletion unsafe when Vitis GUI is open |
| W-A6 | Architecture | WARNING | No validation on `config.json` keys |
| W-A7 | Architecture | WARNING | No Linux board repo path in `create_project.tcl` |
| I-A1 | Architecture | INFO | `hil.egg-info/` on disk (gitignored, no action needed) |
| I-A2 | Architecture | INFO | No `config.json` example for new contributors |
| C-L1 | Code Logic | CRITICAL | `Path.exists()` / `Path.mkdir()` called as class methods |
| W-L1 | Code Logic | WARNING | `create_project.py` subprocess has no output capture |
| W-L2 | Code Logic | WARNING | Dead commented-out code in `create_project.tcl` |
| W-L3 | Code Logic | WARNING | `client.close()` / `os._exit()` ordering is a fragile invariant |
| W-L4 | Code Logic | WARNING | `add_constraints.tcl` skips `update_compile_order` — confirm correct |
| W-L5 | Code Logic | WARNING | `build_vitis.py` checks workspace exists, not platform exists |
| I-L1 | Code Logic | INFO | `add_cores.py` is a stub with no ETA |
| I-L2 | Code Logic | INFO | Vitis script docstrings mix API reference with design rationale |
