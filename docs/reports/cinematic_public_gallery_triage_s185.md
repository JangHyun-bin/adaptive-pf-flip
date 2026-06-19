# S185 Public Gallery Triage

Date: 2026-06-19

## Status

Passed.

Reviewed the S184 public gallery and selected the next visible render target.

## Public Gallery

- URL: `https://cove-grades-tba-tags.trycloudflare.com`
- Local URL: `http://127.0.0.1:8825`
- Publish report: `docs/reports/cinematic_gallery_publish_s184.md`
- S183 gate report:
  `docs/reports/cinematic_secondary_direct_visibility_gate_s183.md`
- S183 comparison report:
  `docs/reports/cinematic_secondary_direct_visibility_gate_comparison_s183.md`

Fresh HTTP checks:

- `https://cove-grades-tba-tags.trycloudflare.com/index.html`: HTTP `200`,
  `5532` bytes
- `https://cove-grades-tba-tags.trycloudflare.com/assets/shot.gif`: HTTP `200`,
  `24035658` bytes
- `https://cove-grades-tba-tags.trycloudflare.com/assets/comparison.png`: HTTP
  `200`, `1289990` bytes
- `https://cove-grades-tba-tags.trycloudflare.com/assets/keyframe_00.png`: HTTP
  `200`, `1159220` bytes

## Keep/Tune Decision

Keep S183.

Evidence:

- Minimum nonblank ratio remains `1.0`.
- Minimum contrast remains `185`.
- Mean luminance delta versus S180 is only `-0.04208423755787294`.
- Mean bright ratio delta versus S180 is only
  `0.00000015070408950615725`.
- Mean highlight ratio delta versus S180 is only
  `0.00000006028163580248458`.

Visual read:

- The direct tan/gold secondary points are less bead-like than S180.
- Soft mist, streaks, and foam readability remain visible.
- The remaining most obvious non-photoreal artifact is no longer secondary
  density. It is water-surface continuity: the render still shows stylized
  reconstruction bands, sheet-like water lobes, and visible surface/overlay
  discontinuities.

## Selected Next Pass

S186: water surface continuity diagnostics and first stabilization pass.

Target:

- Add a renderer-side diagnostic summary for water surface coverage,
  depth-attenuated alpha, reflection strip density, and surface contact rings.
- Add a preset or renderer controls that reduce obvious sheet/band artifacts
  without deleting the fluid body or secondary readability.
- Compare the new pass against S183 and keep exposure/contrast stable.

Implementation direction:

- Start in `tools/render_bridge_blender.py` and `configs/cinematic_presets.json`.
- Keep this as a render-look pass first; do not rerun simulation unless the
  diagnostics prove the cache lacks the needed data.
- Prefer bounded controls that can be summarized in `bridge_summary.json`.
- Reuse `tools/compare_cinematic_frames.py` for S183 versus S186 evidence.

Acceptance:

- 8-frame dry-run/probe and 36-frame warm-cache render pass.
- Nonblank ratio remains `1.0`; contrast does not regress.
- Bright/highlight ratios do not spike.
- Comparison diff is concentrated on water surface continuity artifacts, not
  global exposure, camera, or secondary particle loss.
