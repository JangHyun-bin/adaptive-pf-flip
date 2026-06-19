# S251 Secondary Mist Soft Probe

## Goal

Recover a secondary mist readability candidate after S250 showed that the
stronger S249 probe added too much broad haze.

## Scope

- Add `dam_break_secondary_mist_readability_soft_probe`.
- Leave contact mist curtain unchanged from S246 accepted.
- Leave direct secondary particles unchanged.
- Apply only a small soft mist and streak lift.
- Compare a matched 16-frame baseline against the softer probe.

## Results

- Surface-quality gate: passed.
- Label counts: `normal_rough: 2`, `stable: 14`.
- Stable ratio: `0.875`.
- Blocked labels: `0`.
- Soft mist spray channel: `3.55 -> 3.6`.
- Soft mist foam channel: `3.05 -> 3.1`.
- Soft mist alpha scale: `0.37 -> 0.378`.
- Soft mist max radius: `1.38 -> 1.4`.
- Streak spray channel: `1.18 -> 1.2`.
- Streak foam channel: `0.5 -> 0.51`.
- Contact mist curtain layers: `11 -> 11`.
- Contact mist curtain alpha scale: `0.108 -> 0.108`.
- Contact foam mean delta: `0`.
- Impact ripple mean delta: `0`.
- Secondary streak mean delta: `0`.
- Mean luminance delta: `+0.019665798611114838`.
- Minimum contrast delta: `0.0`.
- Nonblank ratio delta: `0.0`.
- Bright ratio delta: `-2.712673611110993e-07`.
- Highlight ratio delta: `0.0`.
- Calibration `luma_p95` delta: `+0.0625`.
- Calibration `luma_p99` delta: `+0.0625`.
- Calibration `luma_p99.5` delta: `+0.0625`.

## Artifacts

- Probe report:
  `docs/reports/cinematic_secondary_mist_soft_probe_s251.md`
- Gallery report:
  `docs/reports/cinematic_secondary_mist_soft_gallery_s251.md`
- Gallery:
  `build/shots/s251_secondary_mist_soft_probe/gallery/index.html`
- GIF:
  `build/shots/s251_secondary_mist_soft_probe/shot.gif`

## Decision

Promote S251 to 32-frame motion review. It is much subtler than S249, but it
achieves the required direction for this retry: preserve minimum contrast,
coverage, and highlight ratio while still nudging upper luminance percentiles.

## Next

Run S252 as a 32-frame motion review for
`dam_break_secondary_mist_readability_soft_probe` against S246 accepted.
