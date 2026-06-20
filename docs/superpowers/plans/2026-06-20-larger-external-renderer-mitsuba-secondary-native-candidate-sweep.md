# S340 Mitsuba Secondary Native Candidate Sweep

## Goal

Consolidate the recent native Mitsuba secondary candidates into one ranked
summary so the next renderer pass starts from a clear baseline rather than
scattered individual reports.

## Scope

- Add `tools/summarize_mitsuba_secondary_candidate_sweep.py`.
- Read `lsfs_mitsuba_secondary_native_candidate_gap` summaries.
- Rank candidates by max candidate-to-target MAD, then mean candidate-to-target
  MAD.
- Include H2, corrected S338 M1/M2, and S339 B4.
- Record the S335 overlay contract threshold in the summary.

## Command

```powershell
python tools\summarize_mitsuba_secondary_candidate_sweep.py `
  h2=build\shots\s339_mitsuba_runtime_h2_rerender_control_candidate_gap\secondary_native_candidate_gap_summary.json `
  mist_m1=build\shots\s338_mitsuba_secondary_mist_m1_candidate_gap\secondary_native_candidate_gap_summary.json `
  mist_m2=build\shots\s338_mitsuba_secondary_mist_m2_candidate_gap\secondary_native_candidate_gap_summary.json `
  billboard_b4=build\shots\s339_mitsuba_secondary_billboard_b4_candidate_gap\secondary_native_candidate_gap_summary.json `
  --out build\shots\s340_mitsuba_secondary_native_candidate_sweep\candidate_sweep_summary.json `
  --report docs\reports\cinematic_larger_external_renderer_mitsuba_secondary_native_candidate_sweep_s340.md `
  --title "S340 Mitsuba Secondary Native Candidate Sweep"
```

## Outputs

- Summary JSON:
  `build/shots/s340_mitsuba_secondary_native_candidate_sweep/candidate_sweep_summary.json`
- Report:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_native_candidate_sweep_s340.md`
- Summarizer:
  `tools/summarize_mitsuba_secondary_candidate_sweep.py`

## Ranking

| Rank | Candidate | Mean Target MAD | Max Target MAD |
| ---: | --- | ---: | ---: |
| 1 | `mist_m1` | `37.286685796039094` | `66.5063766718107` |
| 2 | `mist_m2` | `37.38058802726338` | `66.78048096707819` |
| 3 | `billboard_b4` | `37.57644900977366` | `67.3997678755144` |
| 4 | `h2` | `37.58172702867798` | `67.40660365226337` |

## Decision

Use `mist_m1` as the current best native Mitsuba secondary baseline. It improves
over H2, but all native geometry candidates remain far behind the S335 overlay
contract max target MAD `18.040229552469135`. The next step should move to a
depth-aware renderer-composite or post-render secondary pass.
