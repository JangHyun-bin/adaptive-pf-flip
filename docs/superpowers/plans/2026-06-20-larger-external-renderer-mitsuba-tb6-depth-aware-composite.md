# S350 Mitsuba TB6 Depth-Aware Composite Refresh

## Goal

Check whether the S348 TB6 native Mitsuba baseline can improve the
depth-aware post-render bridge that previously used S341 C3 as the best public
review target.

## Scope

- Use S348 TB6 native Mitsuba frames as the base render input.
- Reuse the S335 secondary-pass contract as the measured secondary reference.
- Sweep a small set of `native_base_strength` and
  `secondary_native_strength` values around the previous C3 bridge settings.
- Keep this as a post-render bridge measurement; do not treat it as a native
  renderer replacement for screen-space secondary data.

## Commands

Baseline candidate:

```powershell
python tools\build_mitsuba_depth_aware_secondary_composite.py `
  build\shots\s348_mitsuba_tone_bg_tb6\actual_render\mitsuba_render.json `
  build\shots\s335_mitsuba_secondary_pass_contract\secondary_pass_contract.json `
  build\shots\s350_mitsuba_depth_aware_composite_tb6_c1e `
  --native-base-strength 0.135 `
  --secondary-native-strength 0.0185 `
  --mask-blur-radius 2.5 `
  --mask-gain 1.35 `
  --max-target-mean-abs-diff 24 `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_depth_aware_composite_tb6_c1e_s350.md `
  --title "S350 Mitsuba Depth-Aware Composite TB6 C1E"
```

Validation:

```powershell
python tools\validate_mitsuba_depth_aware_secondary_composite.py `
  build\shots\s350_mitsuba_depth_aware_composite_tb6_c1e\depth_aware_secondary_composite_summary.json `
  --out build\shots\s350_mitsuba_depth_aware_composite_tb6_validation\validation.json `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_depth_aware_composite_tb6_validation_s350.md `
  --title "S350 Mitsuba TB6 Depth-Aware Composite Validation"
```

## Outputs

- Candidate reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_composite_tb6_c*_s350.md`
- Validation report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_composite_tb6_validation_s350.md`
- Best gallery:
  `build/shots/s350_mitsuba_depth_aware_composite_tb6_c1e/gallery/index.html`

## Results

| Candidate | Native base | Secondary native | Status | Mean target MAD | Max target MAD | Max contract MAD |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| S341 C3 | `0.14` | `0.02` | `ready` | `11.423722591949588` | `14.571005658436214` | `8.268018904320988` |
| TB6 C1 | `0.14` | `0.02` | `ready` | `11.465766300154321` | `14.592011959876544` | `8.30991512345679` |
| TB6 C1A | `0.13` | `0.018` | `ready` | `11.466292` | `14.419279` | `7.790840` |
| TB6 C1C | `0.12` | `0.017` | `ready` | `11.426700` | `14.609526` | `7.070295` |
| TB6 C1D | `0.125` | `0.018` | `ready` | `11.442775` | `14.563532` | `7.346188` |
| TB6 C1E | `0.135` | `0.0185` | `ready` | `11.464264805169753` | `14.389824459876543` | `8.002740483539094` |
| TB6 C1H | `0.1325` | `0.0185` | `ready` | `11.466355` | `14.414314` | `7.798115` |

C1E is the best by max target MAD. It lowers the previous S341 C3 max target
MAD from `14.571005658436214` to `14.389824459876543` and lowers max contract
MAD from `8.268018904320988` to `8.002740483539094`. Mean target MAD is
slightly worse than S341 C3, so this is a max-frame stability improvement, not
a universal metric win.

## Decision

Use S350 TB6 C1E as the current post-render bridge target when the gate is max
frame error. Keep S341 C3 as a useful reference point for mean target MAD.

This does not change the native-renderer replacement status. TB6 remains the
best native Mitsuba baseline, but the depth-aware bridge is still a post-render
composite until the secondary volume/particle representation is rendered
natively.

## Next

Move back to native data representation rather than more post-render blending:

- tune native water/secondary material around TB6,
- add a proper depth-aware 3D secondary cache/export path,
- package a C1E gallery for external review if a stable public preview is
  needed.
