# S365 Mitsuba Renderer Background Sweep

## Goal

Follow the S364 result by testing renderer-facing background radiance changes
instead of broad post-grade tuning.

The SV1 visibility cache stays fixed. Each candidate is exported and rendered
with Mitsuba, then the same cache is applied and measured against the accepted
target.

## Candidates

- Baseline: `SV1-cache` from S362.
- `B1`: darker/cooler background radiance `0.065,0.083,0.105`.
- `B2`: slightly brighter background radiance `0.095,0.105,0.12`.

## Runtime Note

The default Miniconda `python` no longer has the `mitsuba` module. The working
runtime for this pass is:

`C:/Users/user/AppData/Local/Programs/Python/Python311/python.exe`

with Mitsuba `3.8.0`. The render supervisor still accepts ready manifests after
the known Dr.Jit teardown exit code `3221226505`.

## Result

- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_renderer_background_sweep_summary_s365.md`

| Candidate | Mean Target MAD | Max Target MAD | Decision |
| --- | ---: | ---: | --- |
| `SV1-cache` | `19.103672839506174` | `23.72217142489712` | keep baseline |
| `B2` | `18.129457947530863` | `27.901911651234567` | reject; hard gate regresses |
| `B1` | `21.511723331404323` | `29.499659850823047` | reject |

`B2` improves mean target MAD but worsens the hard max gate. Background radiance
alone is not the right next lever.

## Next

Keep the S357/S362 background baseline. Move to camera/framing or
material/secondary integration rather than more background-only sweeps.
