# S193 Public Gallery Triage

Date: 2026-06-19

## Status

Passed.

Reviewed the S192 public gallery and selected the next visible render target.

## Public Gallery

- URL: `https://emacs-bases-teens-health.trycloudflare.com`
- Local URL: `http://127.0.0.1:8827`
- Publish report: `docs/reports/cinematic_gallery_publish_s192.md`
- S191 gate report: `docs/reports/cinematic_water_mesh_smoothing_s191.md`
- S191 comparison report:
  `docs/reports/cinematic_water_mesh_smoothing_comparison_s191.md`

Fresh HTTP checks:

- `https://emacs-bases-teens-health.trycloudflare.com/index.html`: HTTP `200`,
  `5495` bytes
- `https://emacs-bases-teens-health.trycloudflare.com/assets/shot.gif`: HTTP
  `200`, `23392399` bytes
- `https://emacs-bases-teens-health.trycloudflare.com/assets/comparison.png`:
  HTTP `200`, `2373182` bytes
- `https://emacs-bases-teens-health.trycloudflare.com/assets/keyframe_00.png`:
  HTTP `200`, `1129739` bytes

## Keep/Tune Decision

Keep S191.

Evidence:

- Minimum nonblank ratio remains `1.0`.
- Minimum contrast improves from S186 `181` to S191 `186`.
- Mean luminance delta versus S186 is bounded at `-0.6907726598668944`.
- Mean bright ratio delta versus S186 is only
  `0.000002290702160493845`.
- Mean highlight ratio delta versus S186 is only
  `0.000008921682098765428`.

Visual read:

- The smoothing change is subtle and does not wash out the water body.
- Surface overlay density remains close to S186.
- Some structural sheet/lobe artifacts remain, especially around the
  high-continuity-risk frames identified by S189/S190.

## Selected Next Pass

S194: metric-driven smoothing/occlusion sweep.

Target:

- Compare a small set of bounded water-mesh smoothing factors and a
  renderer-side water-volume occlusion option.
- Use S190 continuity metrics to focus review on the worst continuity frames.
- Avoid blindly increasing smoothing in the main preset until a comparison
  package shows whether stronger smoothing helps or damages water-body detail.

Implementation direction:

- Keep S191 as the accepted public look.
- Generate a short probe matrix from existing cache/summary files.
- Compare S191 against candidate presets with frame sheets and metrics.
- Select one candidate for a full 36-frame render only after the probe matrix.

Acceptance:

- Probe matrix contains at least two smoothing strengths and one occlusion
  candidate.
- Nonblank ratio remains `1.0`.
- Contrast does not regress below S186.
- Selected candidate has a localized diff around water body seams rather than
  secondary particles or global exposure.
