# S337 Mitsuba Secondary Native Candidate Gap

## Goal

Create a measurable gate for deciding when a renderer-native Mitsuba secondary
pass can replace the S334/S335 screen-space overlay hybrid. The gate compares a
native Mitsuba render candidate against the S335 secondary-pass contract and
keeps the replacement decision separate from whether the comparison ran
successfully.

## Scope

- Add `tools/compare_mitsuba_secondary_native_candidate.py`.
- Read a `lsfs_mitsuba_secondary_pass_contract`.
- Read a candidate `lsfs_mitsuba_xml_render` manifest.
- Match frames by `output_frame`.
- Compare each candidate preview against:
  - S335 `overlay_graded` contract frame
  - S328 accepted target frame stored in the contract
- Emit per-frame candidate-to-contract and candidate-to-target diffs.
- Emit a review gallery, GIF, JSON summary, and markdown report.
- Report a `candidate_needs_work` verdict unless the native candidate beats the
  S335 contract on both mean and max target MAD.

## Commands

```powershell
python tools\compare_mitsuba_secondary_native_candidate.py `
  build\shots\s335_mitsuba_secondary_pass_contract\secondary_pass_contract.json `
  build\shots\s333_mitsuba_secondary_halo_h2\actual_render\mitsuba_render.json `
  build\shots\s337_mitsuba_secondary_native_candidate_gap `
  --candidate-label s333_halo_h2 `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_secondary_native_candidate_gap_s337.md `
  --title "S337 Mitsuba Secondary Native Candidate Gap" `
  --next "Use this measured gap to tune the next renderer-native Mitsuba secondary representation; do not replace the S335 overlay contract until a native candidate beats both mean and max target MAD."
```

## Outputs

- Summary JSON:
  `build/shots/s337_mitsuba_secondary_native_candidate_gap/secondary_native_candidate_gap_summary.json`
- Gallery:
  `build/shots/s337_mitsuba_secondary_native_candidate_gap/gallery/index.html`
- Report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_native_candidate_gap_s337.md`
- Comparator:
  `tools/compare_mitsuba_secondary_native_candidate.py`

## Result

- Status: `ready`
- Decision: `candidate_needs_work`
- Frames: `8`
- Missing references: `0`
- Mean candidate-to-contract MAD: `46.4042014692644`
- Max candidate-to-contract MAD: `69.76750578703704`
- Mean candidate-to-target MAD: `37.58172702867798`
- Max candidate-to-target MAD: `67.40660365226337`
- Contract mean overlay MAD: `12.566030735596708`
- Contract max overlay MAD: `18.040229552469135`

## Acceptance

S337 is accepted as a gate because it runs cleanly and records that S333 H2 does
not beat the S335 contract. A future native candidate may replace the overlay
only after both mean and max target MAD improve over the contract.

## Next

Tune or redesign the native Mitsuba secondary representation against this gate.
The likely next pass is a screen-facing or soft-density secondary representation
rather than more opaque sphere/halo proxy tuning.
