# S345 Mitsuba Secondary Mist Billboard Sweep

## Goal

Use the S344 native replacement gate to test whether combining the current best
mist-shell baseline with stronger camera-facing billboards can move the native
Mitsuba output toward the validated C3 bridge.

## Scope

- Reuse `tools/export_external_renderer_mitsuba_xml.py`.
- Keep the S338 M1 camera/background/water/mist settings pinned.
- Add two billboard stress candidates:
  - MB1: moderate opacity and radius.
  - MB2: stronger opacity and larger billboard radius.
- Render both candidates with the existing Mitsuba render tool.
- Compare both against:
  - S335 secondary-pass contract.
  - S341 C3 depth-aware composite bridge through the S344 gate.

## Commands

MB1 export settings:

- `--secondary-billboard-opacity 0.09`
- `--secondary-billboard-radius-scale 2.5`
- `--secondary-billboard-aspect 1.25`

MB2 export settings:

- `--secondary-billboard-opacity 0.18`
- `--secondary-billboard-radius-scale 4.0`
- `--secondary-billboard-aspect 1.4`

Both candidates use the S338 M1 pinned baseline:

- background radiance: `0.16,0.23,0.32`
- water alpha: `0.014`
- secondary proxy limit: `384`
- secondary proxy radius: `0.095`
- secondary opacity: `0.12`
- secondary halo opacity: `0.06`
- secondary halo radius scale: `3.0`
- secondary mist opacity: `0.026`
- secondary mist radius scale: `5.2`
- secondary mist shells: `1`

## Outputs

MB1:

- Export report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_mist_billboard_mb1_export_s345.md`
- Render report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_mist_billboard_mb1_render_s345.md`
- S335 contract gap:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_mist_billboard_mb1_candidate_gap_s345.md`
- C3 bridge gap:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_native_replacement_gap_mb1_s345.md`

MB2:

- Export report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_mist_billboard_mb2_export_s345.md`
- Render report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_mist_billboard_mb2_render_s345.md`
- S335 contract gap:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_mist_billboard_mb2_candidate_gap_s345.md`
- C3 bridge gap:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_depth_aware_native_replacement_gap_mb2_s345.md`

## Results

| Candidate | Mean target MAD | Max target MAD | Mean native-to-C3 MAD | Max native-to-C3 MAD | Decision |
| --- | ---: | ---: | ---: | ---: | --- |
| S338 M1 | `37.286685796039094` | `66.5063766718107` | `40.380344087577164` | `62.06783050411523` | `native_candidate_needs_work` |
| S345 MB1 | `37.244551263503084` | `66.46181069958848` | `40.337390367798356` | `62.021087962962966` | `native_candidate_needs_work` |
| S345 MB2 | `37.13389178240741` | `66.33950488683128` | `40.225236062885806` | `61.84939814814815` | `native_candidate_needs_work` |
| S341 C3 bridge | `11.423722591949588` | `14.571005658436214` | n/a | n/a | validated bridge |

## Decision

MB2 is the best measured native Mitsuba proxy candidate so far, but the
improvement is incremental: max target MAD moves from M1 `66.5063766718107` to
MB2 `66.33950488683128`, still far from the C3 bridge max
`14.571005658436214`. More sphere/mist/billboard proxy strength is not enough
to replace the post-render bridge.

## Next

Move from proxy-only tuning to a more direct renderer-native depth/secondary
representation. The next candidate should use C3/S335 secondary masks as
renderer-pass guidance or a screen-facing/depth-card representation, then
measure against the S344 gate.
