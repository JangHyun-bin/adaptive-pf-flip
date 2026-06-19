# S250 Secondary Mist Motion Review

## Goal

Validate S249 secondary mist readability over the full 32-frame accepted motion
window before deciding whether to promote it.

## Scope

- Reuse S246 accepted water-body thickness as the baseline.
- Render `dam_break_secondary_mist_readability_probe` over source window `8..55`.
- Check surface-quality gate, image metrics, and overlay count parity.

## Results

- Surface-quality gate: passed.
- Label counts: `normal_rough: 3`, `stable: 29`.
- Stable ratio: `0.90625`.
- Blocked labels: `0`.
- Contact foam mean delta: `0`.
- Impact ripple mean delta: `0`.
- Secondary streak mean delta: `0`.
- Mean luminance delta: `+0.4362015787760498`.
- Minimum contrast delta: `-3.0`.
- Mean frame contrast delta: `-1.78125`.
- Nonblank ratio delta: `0.0`.
- Bright ratio delta: `-6.781684027777754e-07`.
- Highlight ratio delta: `-1.220703125000001e-06`.
- Calibration `luma_p95` delta: `+0.34375`.
- Calibration `luma_p99` delta: `+0.1875`.
- Calibration `luma_p99.5` delta: `+0.09375`.

## Artifacts

- Motion review report:
  `docs/reports/cinematic_secondary_mist_motion_review_s250.md`
- Gallery report:
  `docs/reports/cinematic_secondary_mist_motion_gallery_s250.md`
- Gallery:
  `build/shots/s250_secondary_mist_motion_review/gallery/index.html`
- GIF:
  `build/shots/s250_secondary_mist_motion_review/shot.gif`

## Decision

Do not promote S249 as-is. The 32-frame review keeps coverage and raises upper
luminance percentiles, but it drops minimum contrast by `3.0` and mean frame
contrast by `1.78125`. That is too much broad haze for an accepted baseline.

## Next

Run S251 with a softer mist-only probe: reduce or remove the contact mist curtain
increase, keep only a small soft/streak lift, and require non-negative minimum
contrast before promotion.
