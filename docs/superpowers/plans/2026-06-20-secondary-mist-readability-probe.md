# S249 Secondary Mist Readability Probe

## Goal

Test a bounded secondary mist readability pass on top of the accepted S246
cinematic baseline without changing direct secondary particles.

## Scope

- Add `dam_break_secondary_mist_readability_probe`.
- Keep `secondary_direct_pass` unchanged.
- Slightly raise soft spray/foam mist, streaks, and contact mist curtain.
- Compare a matched 16-frame S246 accepted baseline against the probe.

## Results

- Surface-quality gate: passed.
- Label counts: `normal_rough: 2`, `stable: 14`.
- Stable ratio: `0.875`.
- Blocked labels: `0`.
- Soft mist spray channel: `3.55 -> 3.64`.
- Soft mist foam channel: `3.05 -> 3.14`.
- Soft mist alpha scale: `0.37 -> 0.386`.
- Soft mist max radius: `1.38 -> 1.42`.
- Streak spray channel: `1.18 -> 1.22`.
- Streak foam channel: `0.5 -> 0.53`.
- Contact mist curtain layers: `11 -> 12`.
- Contact mist curtain alpha scale: `0.108 -> 0.114`.
- Contact foam mean delta: `0`.
- Impact ripple mean delta: `0`.
- Secondary streak mean delta: `0`.
- Mean luminance delta: `+0.4338905164930651`.
- Minimum contrast delta: `0.0`.
- Nonblank ratio delta: `0.0`.
- Bright ratio delta: `-2.712673611110993e-07`.
- Highlight ratio delta: `-1.3563368055555778e-06`.
- Calibration `luma_p95` delta: `+0.25`.
- Calibration `luma_p99` delta: `+0.0625`.
- Calibration `luma_p99.5` delta: `+0.125`.

## Artifacts

- Probe report:
  `docs/reports/cinematic_secondary_mist_readability_probe_s249.md`
- Gallery report:
  `docs/reports/cinematic_secondary_mist_readability_gallery_s249.md`
- Gallery:
  `build/shots/s249_secondary_mist_readability_probe/gallery/index.html`
- GIF:
  `build/shots/s249_secondary_mist_readability_probe/shot.gif`

## Decision

Keep S249 as a candidate and move it to S250 motion review. The first stronger
mist attempt was too hazy, so the committed probe uses a lower contact curtain
and softer secondary increases. The tuned result preserves minimum contrast and
coverage while improving upper luminance percentiles. The tiny negative
bright/highlight deltas are near the comparison noise floor and should be
checked over 32 frames before acceptance.

## Next

Run S250 as a 32-frame motion review for
`dam_break_secondary_mist_readability_probe` against S246 accepted.
