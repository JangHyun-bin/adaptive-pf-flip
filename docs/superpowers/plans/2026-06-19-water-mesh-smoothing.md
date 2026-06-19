# S191 Water Mesh Smoothing

Date: 2026-06-19

## Goal

Use S190's complete mesh metrics to apply a bounded water mesh smoothing pass
that targets structural sheet/seam artifacts without rerunning simulation.

## Scope

- Add a renderer-side `water_mesh_smoothing_pass`.
- Preserve existing smooth shading behavior when the pass is disabled.
- Add a preset extending `dam_break_water_surface_continuity_stabilized`.
- Validate through dry-run, generated driver compile, probe render, 36-frame
  render, GIF assembly, and S186 comparison.

## Implementation

- `tools/render_bridge_blender.py`
  - Adds `water_mesh_smoothing_pass_summary`.
  - Emits `water_mesh_smoothing_pass` in the bridge summary.
  - Applies Blender Smooth modifier to imported water meshes when enabled.
- `configs/cinematic_presets.json`
  - Adds `dam_break_water_mesh_smoothing`.
  - Uses factor `0.075` and iterations `2`.
  - Slightly lowers surface detail strength while keeping S186 overlay density.

## Result

S191 passed:

- Minimum nonblank ratio: `1.0`
- Minimum contrast: `186`
- Mean luminance delta versus S186: `-0.6907726598668944`
- Mean bright ratio delta versus S186: `0.000002290702160493845`
- Mean highlight ratio delta versus S186: `0.000008921682098765428`

## Follow-Up

S192 should publish the S191 gallery through the existing static gallery and
Cloudflare quick tunnel workflow.
