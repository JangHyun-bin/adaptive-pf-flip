# S186 Water Surface Continuity Stabilization

Date: 2026-06-19

## Goal

Reduce stylized water-surface bands, contact rings, and overlay discontinuities
without hiding the fluid body or undoing the accepted S183 secondary pass.

## Scope

- Add `water_surface_continuity_pass` to the Blender bridge summary path.
- Use the pass to scale existing glint, reflection, contact foam, ripple, and
  scattering controls.
- Add a preset extending `dam_break_secondary_direct_visibility_gate`.
- Preserve the existing external bridge API and simulation cache format.

## Implementation

- `tools/render_bridge_blender.py`
  - Adds `water_surface_continuity_pass_summary`.
  - Applies bounded continuity scales before per-frame overlay count estimates.
  - Adds deterministic `keep_ratio` support for surface contact foam.
  - Emits `water_surface_continuity` diagnostics into `bridge_summary.json`.
- `configs/cinematic_presets.json`
  - Adds `dam_break_water_surface_continuity_stabilized`.
  - Reduces glint/reflection/contact/ripple density and alpha.
  - Keeps water volume scattering active and softens water surface detail.

## Validation

- `python -m py_compile tools\render_bridge_blender.py`
- `python -m json.tool configs\cinematic_presets.json > $null`
- 8-frame dry-run scene generation.
- Generated Blender driver compile.
- 8-frame probe render.
- 36-frame render.
- GIF assembly.
- S183 versus S186 comparison package.
- `git diff --check`

## Result

S186 passed. Nonblank coverage remains complete, highlights were reduced, and
the diff is concentrated on water-surface overlay cues:

- Minimum nonblank ratio: `1.0`
- Minimum contrast: `181`
- Mean luminance delta versus S183: `-1.6593918788580169`
- Mean bright ratio delta versus S183: `-0.0000788182388117284`
- Mean highlight ratio delta versus S183: `-0.00004295066550925926`

## Follow-Up

S187 should publish the S186 gallery through the existing static gallery and
Cloudflare quick tunnel workflow, then triage whether to accept S186 or rebound
surface overlay strength slightly.
