# S188 Public Gallery Triage

Date: 2026-06-19

## Status

Passed.

Reviewed the S187 public gallery and selected the next visible render target.

## Public Gallery

- URL: `https://prizes-inventory-plaintiff-violations.trycloudflare.com`
- Local URL: `http://127.0.0.1:8826`
- Publish report: `docs/reports/cinematic_gallery_publish_s187.md`
- S186 gate report: `docs/reports/cinematic_water_surface_continuity_s186.md`
- S186 comparison report:
  `docs/reports/cinematic_water_surface_continuity_comparison_s186.md`

Fresh HTTP checks:

- `https://prizes-inventory-plaintiff-violations.trycloudflare.com/index.html`:
  HTTP `200`, `5519` bytes
- `https://prizes-inventory-plaintiff-violations.trycloudflare.com/assets/shot.gif`:
  HTTP `200`, `23627133` bytes
- `https://prizes-inventory-plaintiff-violations.trycloudflare.com/assets/comparison.png`:
  HTTP `200`, `2573439` bytes
- `https://prizes-inventory-plaintiff-violations.trycloudflare.com/assets/keyframe_00.png`:
  HTTP `200`, `1134451` bytes

## Keep/Tune Decision

Keep S186.

Evidence:

- Minimum nonblank ratio remains `1.0`.
- Minimum contrast remains acceptable at `181`.
- Mean bright ratio decreases from `0.00023549021026234569` to
  `0.0001566719714506173`.
- Mean highlight ratio decreases from `0.0001398533950617284` to
  `0.00009690272955246914`.
- The comparison diff is concentrated on water surface overlays rather than
  secondary particle loss or global framing changes.

Visual read:

- The water surface reads less crowded than S183.
- Direct secondary particles remain visible enough after S183.
- Remaining artifacts are now structural: the water body still contains
  discontinuous sheet-like lobes, visible mesh/surface bands, and a stylized
  overlay layer that cannot be fully solved by alpha/count tuning.

## Selected Next Pass

S189: surface reconstruction continuity diagnostics.

Target:

- Add diagnostics for water mesh face/vertex counts, occupied-cell counts,
  render-data water-depth spans, and per-frame continuity deltas.
- Add a report/runner mode that can compare S186 cache frames before any more
  look tuning.
- Decide whether the next implementation should smooth the existing mesh,
  adjust the reconstruction/export pipeline, or add a renderer-side water volume
  bridge that hides sparse sheet seams.

Implementation direction:

- Start with diagnostics in the bridge/report layer.
- Avoid another blind material-only preset until the source of the structural
  discontinuity is measured.
- Keep S186 as the current accepted public look.

Acceptance:

- Report identifies the worst continuity frames and relevant mesh/depth metrics.
- The diagnostics are generated from existing cache/summary files without
  rerunning simulation.
- The next implementation target is chosen from measured evidence, not only a
  gallery impression.
