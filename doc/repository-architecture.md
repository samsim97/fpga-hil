# Repository architecture

The full HIL toolchain spans five repositories. This records why they're split the
way they are, so the decision doesn't need re-deriving later.

## This repo (`fpga-hil`): Vivado + Vitis, combined

Despite covering two different AMD toolchains, the hardware (Vivado) and embedded
software (Vitis) tooling live in **one repo**, organized as top-level `vivado/` and
`vitis/` folders rather than as two separate repos.

Why:
- **Hard artifact dependency.** Vitis platform creation consumes the `.xsa` that
  `export-hardware` produces from the Vivado project
  (`vivado/hil/hil/system_wrapper.xsa`). This is a frequently-regenerated build
  artifact, not a stable interface - every meaningful HDL change means a new
  `.xsa`. Splitting the repos means either committing that binary somewhere
  (contradicts "nothing generated gets committed"), wiring up a submodule or CI
  artifact pipeline (real complexity, not proportionate to the project's current
  scale), or a manual copy step (reintroduces exactly the manual handoff that
  scripting `export-hardware` was meant to eliminate).
- **Consistent with this repo's own stated scope.** The README already describes
  the goal as building "an HIL (Hardware in the Loop) platform," not specifically
  a Vivado project - the embedded software is part of that platform, not a
  separate concern.
- **This is reversible.** If independent versioning cadences, separate
  collaborators per toolchain, or some other concrete need shows up later, the
  `vitis/` directory and its `cli/` commands can be extracted into a standalone
  repo at that point. At that point the `.xsa` would become a deliberate,
  versioned interchange artifact between the two repos (the way real hardware/
  software teams typically split this at larger scale) rather than something
  generated and consumed within a single local pipeline.

## Separate repos

These don't share the same kind of hard, frequently-regenerated build-artifact
dependency with `fpga-hil`, so they're kept independent:

- **Delta-sigma DAC simulation** - pure Python modeling of the delta-sigma
  modulator/DAC, no dependency on a Vivado or Vitis project existing at all.
  Likely informs the HDL design rather than depending on it; could outlive or
  predate any particular hardware implementation.
- **cocotb HDL testing** - RTL-level verification of the HDL modules using cocotb
  against a simulator (Icarus/Verilator, etc.), with no dependency on a synthesized
  bitstream or Vivado project. The main benefit of separating this one: someone
  can run the verification suite without installing Vivado or Vitis at all - a
  meaningfully lower barrier to entry for that specific kind of work. Still need
  to decide how it gets read access to `design/hdl/` from this repo (submodule,
  sync script, or a path passed in at test time) - not urgent yet.
- **DAC characterization** - post-implementation analysis of real measurements
  (captured via the HIL software built in this repo) against the simulation model
  above. Consumes data files, not build artifacts; its cadence is "characterize
  whenever hardware exists to measure," decoupled from any build pipeline.

## Where this is referenced

`.agent/skills/vitis-cli/SKILL.md` assumes this combined-repo structure throughout
(e.g. `XSA_PATH` pointing directly into `vivado/hil/`) - if that assumption ever
changes, that skill file needs a pass too, not just this doc.
