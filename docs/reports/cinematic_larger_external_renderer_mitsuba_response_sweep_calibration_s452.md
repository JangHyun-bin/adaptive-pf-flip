# S452 Mitsuba Response Sweep Calibration

Generated UTC: `2026-06-20T14:17:04.463357+00:00`
Summary JSON: `build/shots/s452_mitsuba_response_sweep/calibration/response_calibration_summary.json`
CSV: `build/shots/s452_mitsuba_response_sweep/calibration/response_calibration_candidates.csv`
Status: `ready`

## Ranking

| Rank | Pareto | Candidate | Max Gap MAD | Mean Gap MAD | Max Gap | Patches | Response Faces | Artifact Proxy |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `True` | `S401_CR21_Profile` | 23.552905092592592 | 18.657217962319958 | 182 | 0 | 0 | 182 |
| 2 | `True` | `S409_SF12_H18` | 23.687431841563786 | 18.756908677340533 | 170 | 0 | 0 | 170 |
| 3 | `False` | `S445_GL3_SurfaceGlint` | 23.9334458590535 | 19.204893502443415 | 221 | 0 | 0 | 221 |
| 4 | `False` | `SS1_Native` | 23.951853137860084 | 19.146412117412552 | 170 | 0 | 0 | 170 |
| 5 | `False` | `sw2_compact_high` | 23.954243827160493 | 19.139631156764402 | 177 | 53 | 656 | 345.54 |
| 6 | `False` | `sw1_compact_mid` | 23.954281121399177 | 19.137965454603908 | 176 | 46 | 656 | 291.0 |
| 7 | `False` | `sw3_sparse_high` | 23.954342206790123 | 19.139409159593622 | 177 | 28 | 656 | 279.2 |
| 8 | `False` | `S449_PM3_PerFaceMaterial` | 23.95471322016461 | 19.13953968942901 | 176 | 0 | 656 | 176 |
| 9 | `True` | `S446_SG3_SmoothGlint` | 23.960123456790125 | 19.169528034979425 | 167 | 41 | 0 | 339.20000000000005 |
| 10 | `False` | `S448_MM4_MaterialMask` | 23.963234310699587 | 19.17664359889403 | 179 | 0 | 736 | 179 |

## Pareto Front

- `S401_CR21_Profile`: max MAD `23.552905092592592`, mean MAD `18.657217962319958`, complexity `0.0`
- `S409_SF12_H18`: max MAD `23.687431841563786`, mean MAD `18.756908677340533`, complexity `0.0`
- `S446_SG3_SmoothGlint`: max MAD `23.960123456790125`, mean MAD `19.169528034979425`, complexity `41.0`

## Next

Promote only candidates that improve target gap without adding visible local-response artifacts.
