# S394 Larger External Renderer Mitsuba Secondary Material Scale Sweep

## Goal

Check whether renderer-side secondary reflectance scaling can improve the
target-gap gate enough to replace the existing SS1 native render baseline.

## Candidates

All candidates reuse the S357 SS1 camera, water, sidecar, opacity, billboard,
and proxy settings. Only `--secondary-channel-reflectance-scale` changes:

- `SM45`: `spray=0.45,foam=0.45,bubble=0.45,droplet=0.45`
- `SM60`: `spray=0.60,foam=0.60,bubble=0.60,droplet=0.60`
- `SM75`: `spray=0.75,foam=0.75,bubble=0.75,droplet=0.75`

Each candidate was exported, XML-validated, rendered for `8` frames through the
Mitsuba Python API, scored against the target preview, and scored against the
S350 C1E bridge.

## Results

Target-gap ranking:

| Rank | Candidate | Mean target MAD | Max target MAD | Max diff |
| ---: | --- | ---: | ---: | ---: |
| 1 | `SS1` | `19.146412117412552` | `23.951853137860084` | `170` |
| 2 | `SM75` | `19.222744743441357` | `23.989165380658438` | `226` |
| 3 | `SM60` | `19.222747636959877` | `23.989165380658438` | `226` |
| 4 | `SM45` | `19.22274988747428` | `23.989165380658438` | `226` |

C1E-gap spot summary:

| Candidate | Mean target MAD | Max target MAD | Mean C1E MAD | Max C1E MAD |
| --- | ---: | ---: | ---: | ---: |
| `SM45` | `19.22274988747428` | `23.989165380658438` | `13.724673032407408` | `22.189247685185187` |
| `SM60` | `19.222747636959877` | `23.989165380658438` | `13.724673032407408` | `22.189247685185187` |
| `SM75` | `19.222744743441357` | `23.989165380658438` | `13.724673193158436` | `22.189247685185187` |

## Artifacts

- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_material_scale_sweep_summary_s394.md`
- Candidate reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_material_sm*_*.md`
- Sweep JSON:
  `build/shots/s394_mitsuba_secondary_material_scale_sweep/native_gap_sweep_summary.json`

## Decision

Do not replace SS1 with reflectance-only scaling. All three material-scale
candidates regress the primary max target MAD from SS1 `23.951853137860084` to
`23.989165380658438`, and the three scales are nearly indistinguishable under
the current low-opacity secondary proxy settings.

## Next

Move to opacity/radius or visibility-cache driven material response. Reflectance
scale can stay available as a renderer control, but it is too weak by itself for
the current target-gap objective.
