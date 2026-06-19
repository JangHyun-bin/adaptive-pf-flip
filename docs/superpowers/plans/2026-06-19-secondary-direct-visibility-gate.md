# S183 Secondary Direct Visibility Gate

Date: 2026-06-19

## Goal

Reduce bead-like direct secondary particles in the S180 cinematic render without
removing the softer mist and streak layers that make spray and foam readable.

## Scope

- Add renderer-side `secondary_direct_pass` controls.
- Keep the pass bounded to direct sphere emission only.
- Add a preset extending `dam_break_secondary_mist_debeading`.
- Validate through dry-run, 8-frame probe, 36-frame render, GIF assembly, and
  S180 comparison.

## Implementation

- `tools/render_bridge_blender.py`
  - Emits `secondary_direct_pass` in the scene spec and bridge summary.
  - Clamps per-channel keep ratios and max-count scale.
  - Applies deterministic direct-secondary keep/dropout inside
    `add_secondary_particles`.
  - Leaves `add_secondary_soft_pass` and `add_secondary_streak_pass` unchanged.
- `configs/cinematic_presets.json`
  - Adds `dam_break_secondary_direct_visibility_gate`.
  - Sets direct keep ratios for droplet, spray, foam, and bubble.
  - Slightly rebalances soft/streak visibility so direct thinning does not erase
    secondary readability.

## Validation

- `python -m py_compile tools\render_bridge_blender.py`
- `python -m json.tool configs\cinematic_presets.json > $null`
- 8-frame dry-run scene generation.
- Generated Blender driver compile.
- 8-frame probe render.
- 36-frame render.
- GIF assembly.
- S180 versus S183 comparison package.
- `git diff --check`

## Result

S183 passed. The comparison metrics remain stable versus S180, and the visual
diff is concentrated on direct secondary particles:

- Minimum nonblank ratio: `1.0`
- Minimum contrast: `185`
- Mean luminance delta: `-0.04208423755787294`
- Mean bright ratio delta: `0.00000015070408950615725`
- Mean highlight ratio delta: `0.00000006028163580248458`

## Follow-Up

S184 should publish the S183 gallery through the existing static gallery and
Cloudflare quick tunnel workflow, then triage whether the next visible target is
surface reconstruction continuity or further secondary material tuning.
