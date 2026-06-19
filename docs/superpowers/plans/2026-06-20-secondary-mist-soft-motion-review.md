# S252 Secondary Mist Soft Motion Review

## Goal

Validate S251's softer secondary mist probe over the 32-frame accepted motion
window.

## Scope

- Reuse S246 accepted water-body thickness as the baseline.
- Render `dam_break_secondary_mist_readability_soft_probe` over source window
  `8..55`.
- Check surface-quality gate, image metrics, and overlay count parity.

## Results

- Surface-quality gate: passed.
- Label counts: `normal_rough: 3`, `stable: 29`.
- Stable ratio: `0.90625`.
- Blocked labels: `0`.
- Contact foam mean delta: `0`.
- Impact ripple mean delta: `0`.
- Secondary streak mean delta: `0`.
- Mean luminance delta: `+0.020624593098958144`.
- Minimum contrast delta: `0.0`.
- Mean frame contrast delta: `0.0`.
- Nonblank ratio delta: `0.0`.
- Bright ratio delta: `-1.3563368055557676e-07`.
- Highlight ratio delta: `0.0`.
- Calibration `luma_p95` delta: `+0.125`.
- Calibration `luma_p99` delta: `+0.03125`.
- Calibration `luma_p99.5` delta: `-0.03125`.

## Artifacts

- Motion review report:
  `docs/reports/cinematic_secondary_mist_soft_motion_review_s252.md`
- Gallery report:
  `docs/reports/cinematic_secondary_mist_soft_motion_gallery_s252.md`
- Gallery:
  `build/shots/s252_secondary_mist_soft_motion_review/gallery/index.html`
- GIF:
  `build/shots/s252_secondary_mist_soft_motion_review/shot.gif`

## Decision

Do not promote S251. It is stable, but the visible improvement is too small to
justify adding another accepted-preset change, and `luma_p99.5` has a tiny
negative delta. Keep the evidence, then move to a more visible pass.

## Next

Switch from secondary mist tuning to a more impactful visual pass. The next
recommended target is accepted-baseline presentation: a publishable S246 review
page/package or a larger shot composition pass.
