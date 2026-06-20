# S354 Mitsuba Secondary 3D Import Pass

## Goal

Consume the S353 depth-aware 3D secondary sidecar in the Mitsuba XML exporter
instead of re-sampling secondary particles directly from the large CSV stream.

## Scope

- Extend `tools/export_external_renderer_mitsuba_xml.py` with
  `--secondary-3d-sidecar`.
- Keep existing CSV sampling behavior as the default.
- When a sidecar is provided, map frames by `output_frame`, load each JSONL
  sidecar file, and emit native secondary sphere proxies from sidecar radius
  and position records.
- Test three sphere-only opacity candidates:
  - SI1: opacity `0.05`
  - SI2: opacity `0.02`
  - SI3: opacity `0.01`
- Keep MW7 as the no-secondary-proxy control baseline.

## Outputs

- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_3d_import_sweep_summary_s354.md`
- Per-candidate export reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_3d_import_si*_export_s354.md`
- Per-candidate render reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_3d_import_si*_render_s354.md`
- Per-candidate S335 contract gaps:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_3d_import_si*_candidate_gap_s354.md`
- Per-candidate S350 C1E bridge gaps:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_3d_import_si*_c1e_gap_s354.md`

## Results

| Candidate | Mean target MAD | Max target MAD | Max contract MAD | Mean native-to-C1E MAD | Max native-to-C1E MAD |
| --- | ---: | ---: | ---: | ---: | ---: |
| MW7 | `19.146286` | `23.951993` | `25.512461` | `13.605084` | `22.125309` |
| SI1 | `19.148799` | `23.955634` | `25.505369` | `13.599584` | `22.126921` |
| SI2 | `19.147831` | `23.954052` | `25.508183` | `13.600666` | `22.126199` |
| SI3 | `19.147658` | `23.953638` | `25.508993` | `13.601172` | `22.126016` |

The import path works: SI1/SI2/SI3 export `2877` sidecar particles across `8`
frames and render successfully. Metric-wise, SI3 is the best sidecar import
candidate by max target MAD, but it still does not beat MW7's max target gate.
SI1 slightly improves max contract MAD and mean native-to-C1E MAD, so the
sidecar path is useful, but the current sphere-only material is not acceptance
ready.

## Decision

Keep the S353/S354 sidecar import path. Do not promote SI1/SI2/SI3 over MW7 as
the native visual baseline yet.

The next step should tune the sidecar import representation itself: radius
scale, channel-specific opacity, depth attenuation, and possibly billboard or
volume shells driven by sidecar depth instead of simple uniform sphere proxies.

## Next

Run a sidecar-material tuning pass with channel-specific radius/opacity and
depth attenuation. The gate remains max target MAD against S350 C1E and S335.
