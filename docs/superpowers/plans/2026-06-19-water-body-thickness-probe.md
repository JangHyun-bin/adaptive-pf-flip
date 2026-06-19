# S244 Water Body Thickness Probe

## Goal

Test a bounded water-body thickness/refraction look on top of the accepted S242
baseline without changing accepted foam, ripple, glint, reflection, or direct
secondary particle behavior.

## Scope

- Add `dam_break_water_body_thickness_probe` as a probe preset.
- Keep accepted foam/highlight overlay controls inherited from
  `dam_break_water_mesh_smoothing`.
- Adjust only water material depth/alpha/transmission, water volume scatter
  material, volume scattering layers, and water surface detail.
- Run a matched 16-frame accepted baseline and probe comparison.

## Results

- Surface-quality gate: passed.
- Label counts: `normal_rough: 2`, `stable: 14`.
- Stable ratio: `0.875`.
- Blocked labels: `0`.
- Water volume scatter layers: `18 -> 20`.
- Water volume scatter alpha scale: `0.324 -> 0.3456`.
- Water volume occlusion: disabled in accepted and probe.
- Contact foam mean delta: `0`.
- Impact ripple mean delta: `0`.
- Secondary streak mean delta: `0`.
- Mean luminance delta: `+0.3961309136284683`.
- Bright ratio delta: `+3.065321180555552e-05`.
- Highlight ratio delta: `+1.6818576388888902e-05`.
- Nonblank ratio delta: `0.0`.
- Minimum contrast delta: `-1.0`.
- Calibration `luma_p95` delta: `+0.5625`.
- Calibration `luma_p99` delta: `+0.125`.
- Calibration `luma_p99.5` delta: `-0.125`.

## Artifacts

- Probe report:
  `docs/reports/cinematic_water_body_thickness_probe_s244.md`
- Gallery report:
  `docs/reports/cinematic_water_body_thickness_gallery_s244.md`
- Gallery:
  `build/shots/s244_water_body_thickness_probe/gallery/index.html`
- GIF:
  `build/shots/s244_water_body_thickness_probe/shot.gif`

## Decision

Keep S244 as a candidate, not an accepted preset change. The second tuned probe
adds a visible depth cue and improves upper-mid/bright ratios without changing
foam/ripple/streak counts or coverage. The small minimum contrast and `luma_p99.5`
drops mean it needs a 32-frame motion review before promotion.

## Next

Run S245 as a 32-frame motion review for
`dam_break_water_body_thickness_probe` against S242 accepted.
