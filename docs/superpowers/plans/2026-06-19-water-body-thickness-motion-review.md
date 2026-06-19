# S245 Water Body Thickness Motion Review

## Goal

Validate the S244 water-body thickness/refraction probe over the full 32-frame
accepted motion window before accepted-preset promotion.

## Scope

- Reuse S242 accepted foam/readability as the baseline.
- Render `dam_break_water_body_thickness_probe` over source window `8..55`.
- Check surface-quality gate, image metrics, water volume pass deltas, and
  foam/ripple/streak count parity.

## Results

- Surface-quality gate: passed.
- Label counts: `normal_rough: 3`, `stable: 29`.
- Stable ratio: `0.90625`.
- Blocked labels: `0`.
- Water volume scatter layers: `18 -> 20`.
- Water volume scatter alpha scale: `0.324 -> 0.3456`.
- Water volume occlusion enabled: `false -> false`.
- Contact foam mean delta: `0`.
- Impact ripple mean delta: `0`.
- Secondary streak mean delta: `0`.
- Mean luminance delta: `+0.37631863064235915`.
- Minimum contrast delta: `+1.0`.
- Nonblank ratio delta: `0.0`.
- Bright ratio delta: `+5.018446180555557e-05`.
- Highlight ratio delta: `+2.8754340277777787e-05`.
- Calibration `luma_p95` delta: `+0.5`.
- Calibration `luma_p99` delta: `+0.09375`.
- Calibration `luma_p99.5` delta: `0.0`.

## Artifacts

- Motion review report:
  `docs/reports/cinematic_water_body_thickness_motion_review_s245.md`
- Gallery report:
  `docs/reports/cinematic_water_body_thickness_motion_gallery_s245.md`
- Gallery:
  `build/shots/s245_water_body_thickness_motion_review/gallery/index.html`
- GIF:
  `build/shots/s245_water_body_thickness_motion_review/shot.gif`

## Decision

Promote the probe in S246. The 32-frame review resolves the S244 watch items:
minimum contrast is positive, `luma_p99.5` is unchanged, coverage is unchanged,
and foam/ripple/streak counts stay fixed. The volume cue adds brightness and
upper-tail energy without broad instability in this accepted window.

## Next

Fold `dam_break_water_body_thickness_probe` into
`dam_break_water_mesh_smoothing` in S246, then run accepted-preset parity against
S245.
