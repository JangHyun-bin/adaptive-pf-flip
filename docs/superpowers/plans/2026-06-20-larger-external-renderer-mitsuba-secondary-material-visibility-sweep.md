# S395 Larger External Renderer Mitsuba Secondary Material Visibility Sweep

## Goal

Check whether renderer-side opacity/radius visibility boosts improve the native
Mitsuba target-gap gate after S394 showed reflectance-only scaling was too weak.

## Candidates

All candidates reuse the S357 SS1 camera, water, sidecar, and proxy baseline.

- `OV1`: opacity boost
  - `secondary-3d-channel-opacity`: `spray=0.002,foam=0.03,bubble=0.02,droplet=0.002`
  - `secondary-billboard-opacity`: `0.004`
  - radius settings unchanged
- `RV1`: radius boost
  - `secondary-3d-radius-scale`: `0.24`
  - `secondary-billboard-radius-scale`: `2.8`
  - opacity settings unchanged
- `OR1`: opacity + radius boost
  - combines `OV1` opacity settings with `RV1` radius settings

Each candidate was exported, XML-validated, rendered for `8` frames through the
Mitsuba Python API, scored against the target preview, and scored against the
S350 C1E bridge.

## Results

Target-gap ranking:

| Rank | Candidate | Mean target MAD | Max target MAD | Max diff |
| ---: | --- | ---: | ---: | ---: |
| 1 | `SS1` | `19.146412117412552` | `23.951853137860084` | `170` |
| 2 | `OV1` | `19.22269949202675` | `23.98887281378601` | `226` |
| 3 | `RV1` | `19.223276990097737` | `23.989178883744856` | `226` |
| 4 | `OR1` | `19.22330608603395` | `23.989264403292182` | `226` |

C1E-gap spot summary:

| Candidate | Mean target MAD | Max target MAD | Mean C1E MAD | Max C1E MAD |
| --- | ---: | ---: | ---: | ---: |
| `OV1` | `19.22269949202675` | `23.98887281378601` | `13.724645624356995` | `22.189060570987653` |
| `RV1` | `19.223276990097737` | `23.989178883744856` | `13.724978620113168` | `22.18950552983539` |
| `OR1` | `19.22330608603395` | `23.989264403292182` | `13.724990194187242` | `22.189588477366254` |

## Artifacts

- Sweep summary:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_material_visibility_sweep_summary_s395.md`
- Candidate reports:
  `docs/reports/cinematic_larger_external_renderer_mitsuba_secondary_material_{ov1,rv1,or1}_*.md`
- Sweep JSON:
  `build/shots/s395_mitsuba_secondary_material_visibility_sweep/native_gap_sweep_summary.json`

## Decision

Do not replace SS1 with direct opacity/radius visibility boosts. OV1 is the best
new candidate, but it still regresses max target MAD from SS1
`23.951853137860084` to `23.98887281378601`. Radius expansion worsens the gate
slightly more, and combining opacity with radius is worst among the three.

## Next

Stop broad material visibility boosts. The next viable renderer-side path is to
use the already successful screen/visibility evidence, such as SV1-cache or the
CR21 channel-local mask, to drive a localized material/screen response instead
of changing all secondary proxies globally.
