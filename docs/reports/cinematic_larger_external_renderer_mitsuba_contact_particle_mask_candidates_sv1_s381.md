# S381 Mitsuba Contact Particle Mask Candidates SV1

Generated UTC: `2026-06-20T06:19:59.527155+00:00`
Summary JSON: `build/shots/s381_mitsuba_contact_particle_mask_candidates_sv1/contact_particle_mask_candidate_summary.json`
CSV: `build/shots/s381_mitsuba_contact_particle_mask_candidates_sv1/contact_particle_mask_candidates.csv`
Gallery: `build/shots/s381_mitsuba_contact_particle_mask_candidates_sv1/gallery/index.html`
Public quick-tunnel review: `https://motivation-asthma-gilbert-gabriel.trycloudflare.com/index.html`
Status: `contact_candidate_below_best`

## Checks

- Frames: `8`
- Candidates: `63`
- Contact candidates: `60`
- Best dark-secondary mask: `secondary_source_luma_0_75` F1 `0.6121749824314828`
- Best contact dark-secondary mask: `contact_foam_or_ripple_secondary_source_luma_0_85` F1 `0.27131367292225206`
- Best highlight mask: `source_highlight_120` F1 `0.8881401617250673`

## Top Contact Dark Secondary Masks

| Rank | Candidate | Precision | Recall | F1 | Candidate Coverage |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `contact_foam_or_ripple_secondary_source_luma_0_85` | 0.632975 | 0.172661 | 0.271314 | 0.000964 |
| 2 | `contact_foam_secondary_source_luma_0_85` | 0.677978 | 0.133625 | 0.223248 | 0.000696 |
| 3 | `contact_foam_or_ripple_secondary_source_luma_0_75` | 0.953625 | 0.122091 | 0.216468 | 0.000452 |
| 4 | `contact_foam_or_ripple_secondary_source_luma_20_75` | 0.953625 | 0.122091 | 0.216468 | 0.000452 |
| 5 | `contact_foam_or_ripple_source_luma_0_75` | 0.545593 | 0.122091 | 0.199532 | 0.000791 |
| 6 | `contact_foam_or_ripple_source_luma_20_75` | 0.545593 | 0.122091 | 0.199532 | 0.000791 |
| 7 | `contact_foam_or_ripple_source_luma_0_85` | 0.225450 | 0.172661 | 0.195556 | 0.002706 |
| 8 | `impact_ripple_secondary_source_luma_0_85` | 0.652899 | 0.106804 | 0.183578 | 0.000578 |
| 9 | `contact_foam_secondary_source_luma_0_75` | 0.975678 | 0.095817 | 0.174497 | 0.000347 |
| 10 | `contact_foam_secondary_source_luma_20_75` | 0.975678 | 0.095817 | 0.174497 | 0.000347 |
| 11 | `contact_foam_source_luma_0_85` | 0.233290 | 0.133625 | 0.169921 | 0.002024 |
| 12 | `contact_foam_source_luma_0_75` | 0.525843 | 0.095817 | 0.162097 | 0.000644 |

## Top Contact Highlight Masks

| Rank | Candidate | Precision | Recall | F1 | Candidate Coverage |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `impact_ripple_spray` | 0.005047 | 0.006660 | 0.005742 | 0.008123 |
| 2 | `impact_ripple` | 0.003431 | 0.008501 | 0.004889 | 0.015250 |
| 3 | `contact_foam_or_ripple` | 0.002662 | 0.011635 | 0.004332 | 0.026907 |
| 4 | `contact_foam` | 0.001606 | 0.005093 | 0.002442 | 0.019515 |
| 5 | `contact_foam_source_luma_20_105` | 0.001382 | 0.004152 | 0.002074 | 0.018498 |
| 6 | `contact_foam_or_ripple_source_luma_20_105` | 0.001191 | 0.004936 | 0.001919 | 0.025515 |
| 7 | `impact_ripple_foam` | 0.001290 | 0.001920 | 0.001543 | 0.009156 |
| 8 | `impact_ripple_source_luma_20_105` | 0.001043 | 0.002429 | 0.001460 | 0.014330 |

## Radius Sweep

| Setting | Best Contact Dark Mask | Precision | Recall | F1 |
| --- | --- | ---: | ---: | ---: |
| `r100` | `contact_foam_or_ripple_secondary_source_luma_0_85` | 0.632975 | 0.172661 | 0.271314 |
| `r150` | `contact_foam_or_ripple_secondary_source_luma_0_85` | 0.607002 | 0.209445 | 0.311431 |
| `r250` | `contact_foam_or_ripple_secondary_source_luma_0_85` | 0.567958 | 0.263223 | 0.359728 |
| `r400` | `contact_foam_or_ripple_secondary_source_luma_0_85` | 0.545306 | 0.319116 | 0.402618 |

The best enlarged contact/ripple mask remains below the DS6-equivalent
`secondary_source_luma_0_75` baseline at F1 `0.612175`.

## Next

Contact/ripple masks are only promoted if they beat DS6; otherwise move to renderer AOV or a bounded material response using DS6 as the mask.
