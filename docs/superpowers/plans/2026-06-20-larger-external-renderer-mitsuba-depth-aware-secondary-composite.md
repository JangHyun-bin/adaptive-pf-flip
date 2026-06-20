# S341 Mitsuba Depth-Aware Secondary Composite

## Goal

Move beyond pure native secondary geometry by adding a post-render,
depth-aware secondary composite bridge. The bridge should keep the S335
screen-space contract visually stable while injecting controlled detail from
the current best native Mitsuba secondary baseline, S338 M1.

## Scope

- Add `tools/build_mitsuba_depth_aware_secondary_composite.py`.
- Use S338 M1 actual Mitsuba render as the native input.
- Use S335 `lsfs_mitsuba_secondary_pass_contract` as the contract input.
- Build a secondary alpha/depth proxy from the contract secondary layer.
- Blend native graded pixels into the contract output with:
  - higher native weight away from secondary pixels
  - lower native weight near secondary alpha
  - optional luminance weighting
- Emit composite frames, native-weight masks, target diffs, strips, gallery,
  JSON summary, and markdown report.

## Commands

Naive overlay baseline:

```powershell
python tools\build_mitsuba_render_secondary_overlay.py `
  build\shots\s338_mitsuba_secondary_mist_m1\actual_render\mitsuba_render.json `
  build\shots\s327_mitsuba_renderer_handoff_bundle\handoff_manifest.json `
  build\shots\s328_mitsuba_renderer_target_preview\renderer_target_preview_summary.json `
  build\shots\s341_mitsuba_mist_m1_overlay_baseline `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_mist_m1_overlay_baseline_s341.md `
  --title "S341 Mitsuba Mist M1 Overlay Baseline"
```

Best depth-aware candidate C3:

```powershell
python tools\build_mitsuba_depth_aware_secondary_composite.py `
  build\shots\s338_mitsuba_secondary_mist_m1\actual_render\mitsuba_render.json `
  build\shots\s335_mitsuba_secondary_pass_contract\secondary_pass_contract.json `
  build\shots\s341_mitsuba_depth_aware_composite_c3 `
  --native-base-strength 0.14 `
  --secondary-native-strength 0.02 `
  --mask-blur-radius 2.5 `
  --mask-gain 1.35 `
  --max-target-mean-abs-diff 24 `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_depth_aware_composite_c3_s341.md `
  --title "S341 Mitsuba Depth-Aware Composite C3"
```

## Outputs

- Tool:
  `tools/build_mitsuba_depth_aware_secondary_composite.py`
- Naive overlay baseline report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_mist_m1_overlay_baseline_s341.md`
- C1-C4 reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_composite_c1_s341.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_composite_c2_s341.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_composite_c3_s341.md`
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_composite_c4_s341.md`
- Best gallery:
  `build/shots/s341_mitsuba_depth_aware_composite_c3/gallery/index.html`

## Results

| Candidate | Native base | Secondary native | Mean Target MAD | Max Target MAD | Max Contract MAD |
| --- | ---: | ---: | ---: | ---: | ---: |
| Naive overlay baseline | n/a | n/a | `29.154523855452673` | `60.98076067386831` | n/a |
| C1 | `0.045` | `0.006` | `11.936789801954733` | `16.35688014403292` | `2.7353755144032923` |
| C2 | `0.08` | `0.012` | `11.587655446244856` | `15.450580632716049` | `4.72353587962963` |
| C3 | `0.14` | `0.02` | `11.423722591949588` | `14.571005658436214` | `8.268018904320988` |
| C4 | `0.25` | `0.035` | `12.195964104295268` | `19.998582175925925` | `14.806318158436214` |

S335 contract max target MAD is `18.040229552469135`.

## Decision

Use C3 as the current post-render bridge baseline. It improves over the S335
contract while retaining measured native contribution from S338 M1. C4 adds too
much native influence and loses the contract gate. The next step should validate
C3 with a dedicated contract/composite validator and then package/publish the
C3 gallery for visual inspection.
