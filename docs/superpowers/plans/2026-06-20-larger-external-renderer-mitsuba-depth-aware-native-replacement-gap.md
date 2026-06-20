# S344 Mitsuba Depth-Aware Native Replacement Gap

## Goal

Create a renderer-native replacement gate that compares an actual Mitsuba render
against the validated S341 C3 depth-aware composite bridge.

## Scope

- Add `tools/compare_mitsuba_native_to_depth_aware_composite.py`.
- Use the S341 C3 composite summary as the bridge target.
- Use S338 M1 as the current best native Mitsuba secondary baseline.
- Compare native candidate frames against both:
  - the S341 C3 bridge composite
  - the accepted renderer target frame
- Emit native-vs-bridge diffs, native-vs-target diffs, strips, gallery,
  summary JSON, and markdown report.

## Command

```powershell
python tools\compare_mitsuba_native_to_depth_aware_composite.py `
  build\shots\s341_mitsuba_depth_aware_composite_c3\depth_aware_secondary_composite_summary.json `
  build\shots\s338_mitsuba_secondary_mist_m1\actual_render\mitsuba_render.json `
  build\shots\s344_mitsuba_depth_aware_native_replacement_gap_m1 `
  --candidate-label mist_m1 `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_depth_aware_native_replacement_gap_s344.md `
  --title "S344 Mitsuba Depth-Aware Native Replacement Gap M1" `
  --next "Use this gate to drive the next renderer-native secondary pass; native candidates should beat the C3 bridge mean and max target MAD before replacing the post-render bridge."
```

## Outputs

- Tool:
  `tools/compare_mitsuba_native_to_depth_aware_composite.py`
- Gap report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_native_replacement_gap_s344.md`
- Gap summary:
  `build/shots/s344_mitsuba_depth_aware_native_replacement_gap_m1/depth_aware_native_replacement_gap_summary.json`
- Gap gallery:
  `build/shots/s344_mitsuba_depth_aware_native_replacement_gap_m1/gallery/index.html`

## Results

The S338 M1 native render is still not close to replacing the C3 bridge:

| Metric | Native M1 | C3 bridge |
| --- | ---: | ---: |
| Mean target MAD | `37.286685796039094` | `11.423722591949588` |
| Max target MAD | `66.5063766718107` | `14.571005658436214` |

Additional native-to-bridge distance:

- Mean native-to-bridge MAD: `40.380344087577164`
- Max native-to-bridge MAD: `62.06783050411523`
- Frames: `8`
- Missing references: `0`
- Decision: `native_candidate_needs_work`

## Decision

S344 does not improve the visual baseline directly. It adds the gate needed for
the next renderer-native secondary pass: a native render should not replace the
S341 C3 post-render bridge until it beats both C3 mean target MAD and C3 max
target MAD.

## Next

Use this gap to design the first renderer-native depth/secondary pass. The next
candidate should change the native Mitsuba output, not just post-composite it.
