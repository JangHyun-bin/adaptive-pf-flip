# S451 Mitsuba Response Calibration Summary

Generated UTC: `2026-06-20T14:11:41.033559+00:00`
Summary JSON: `build/reports/s451_mitsuba_response_calibration_summary/response_calibration_summary.json`
CSV: `build/reports/s451_mitsuba_response_calibration_summary/response_calibration_candidates.csv`
Status: `ready`

## Ranking

| Rank | Pareto | Candidate | Max Gap MAD | Mean Gap MAD | Max Gap | Patches | Response Faces | Artifact Proxy |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | `True` | `S401_CR21_Profile` | 23.552905092592592 | 18.657217962319958 | 182 | 0 | 0 | 182 |
| 2 | `True` | `S409_SF12_H18` | 23.687431841563786 | 18.756908677340533 | 170 | 0 | 0 | 170 |
| 3 | `False` | `S445_GL3_SurfaceGlint` | 23.9334458590535 | 19.204893502443415 | 221 | 0 | 0 | 221 |
| 4 | `False` | `SS1_Native` | 23.951853137860084 | 19.146412117412552 | 170 | 0 | 0 | 170 |
| 5 | `False` | `S450_HY3_PM3SoftPatch` | 23.954352494855968 | 19.13657873585391 | 176 | 41 | 656 | 252.67000000000002 |
| 6 | `False` | `S449_PM3_PerFaceMaterial` | 23.95471322016461 | 19.13953968942901 | 176 | 0 | 656 | 176 |
| 7 | `False` | `S450_HY2_PM3SoftPatch` | 23.955955504115227 | 19.14057010352366 | 177 | 15 | 656 | 184.5 |
| 8 | `True` | `S446_SG3_SmoothGlint` | 23.960123456790125 | 19.169528034979425 | 167 | 41 | 0 | 339.20000000000005 |
| 9 | `False` | `S450_HY1_PM3SoftPatch` | 23.96079732510288 | 19.143168724279835 | 176 | 21 | 656 | 183.35 |
| 10 | `False` | `S448_MM4_MaterialMask` | 23.963234310699587 | 19.17664359889403 | 179 | 0 | 736 | 179 |

## Pareto Front

- `S401_CR21_Profile`: max MAD `23.552905092592592`, mean MAD `18.657217962319958`, complexity `0.0`
- `S409_SF12_H18`: max MAD `23.687431841563786`, mean MAD `18.756908677340533`, complexity `0.0`
- `S446_SG3_SmoothGlint`: max MAD `23.960123456790125`, mean MAD `19.169528034979425`, complexity `41.0`

## Next

Use the Pareto/frontier data to drive a bounded parameter sweep rather than another manual one-off render.
