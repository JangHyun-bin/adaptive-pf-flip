# S423 Mitsuba Source Response Intent Channel Analysis

Generated UTC: `2026-06-20T11:24:32.563864+00:00`
Summary JSON: `build/shots/s423_mitsuba_source_response_intent_channel_analysis/source_response_mask_channel_summary.json`
CSV: `build/shots/s423_mitsuba_source_response_intent_channel_analysis/source_response_mask_channel_candidates.csv`
Gallery: `build/shots/s423_mitsuba_source_response_intent_channel_analysis/gallery/index.html`
Public URL: `https://barely-wiring-ongoing-trusted.trycloudflare.com/index.html`
Status: `ready`

## Findings

- S409 channel-band is strongly explained by projected spray/foam evidence: best candidate `spray` has F1 `0.564300`, precision `0.437650`, recall `0.794102`; `spray_or_foam` reaches recall `1.000000`.
- S409 union is still mostly a spray/foam attenuation intent: best candidate `spray` has F1 `0.480093`, while highlight overlap with secondary channels is near zero.
- S401 highlight and S409 highlight should stay separate from secondary material attenuation. Their best secondary overlap F1 is only `0.008123`.
- S401 CR21 dark-primary/channel-band masks are weakly explained by projected secondary channels, so CR21 should remain an upper-bound post-response reference rather than the next renderer-native target.

## Checks

- Frames: `56`
- Mask sources: `7`
- Candidate masks: `35`
- GIF bytes: `24.66 MB`
- Local gallery HTTP: `200`
- Public index HTTP: `200`
- Public GIF HTTP: `200`

## Top Candidates By Mask

### S401_CR21_highlight

| Rank | Candidate | Precision | Recall | F1 | Coverage |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `spray_density_ge_8` | 0.004530 | 0.039263 | 0.008123 | 0.034599 |
| 2 | `all_secondary_channels_density_ge_8` | 0.003930 | 0.045424 | 0.007234 | 0.046142 |
| 3 | `spray_or_foam_density_ge_8` | 0.003658 | 0.039263 | 0.006692 | 0.042847 |
| 4 | `spray_density_ge_16` | 0.003111 | 0.024645 | 0.005524 | 0.031626 |
| 5 | `all_secondary_channels_density_ge_16` | 0.002632 | 0.028390 | 0.004818 | 0.043052 |
| 6 | `spray_or_foam_density_ge_16` | 0.002458 | 0.024645 | 0.004471 | 0.040019 |
| 7 | `bubble_density_ge_8` | 0.002401 | 0.006705 | 0.003536 | 0.011146 |
| 8 | `bubble_density_ge_16` | 0.001590 | 0.003805 | 0.002243 | 0.009553 |

### S401_CR21_dark_primary

| Rank | Candidate | Precision | Recall | F1 | Coverage |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `spray_density_ge_32` | 0.043784 | 0.604929 | 0.081658 | 0.027035 |
| 2 | `spray_density_ge_16` | 0.043047 | 0.695749 | 0.081078 | 0.031626 |
| 3 | `spray_or_foam_density_ge_16` | 0.042123 | 0.861491 | 0.080318 | 0.040019 |
| 4 | `all_secondary_channels_density_ge_16` | 0.041950 | 0.922982 | 0.080253 | 0.043052 |
| 5 | `spray_or_foam_density_ge_8` | 0.041509 | 0.908934 | 0.079393 | 0.042847 |
| 6 | `spray_density_ge_8` | 0.041816 | 0.739372 | 0.079155 | 0.034599 |
| 7 | `all_secondary_channels_density_ge_32` | 0.041566 | 0.816636 | 0.079106 | 0.038443 |
| 8 | `spray_or_foam_density_ge_32` | 0.041586 | 0.758349 | 0.078848 | 0.035682 |

### S401_CR21_channel_band

| Rank | Candidate | Precision | Recall | F1 | Coverage |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `foam_or_bubble` | 0.019573 | 0.638593 | 0.037982 | 0.014758 |
| 2 | `foam` | 0.018936 | 0.505864 | 0.036506 | 0.012084 |
| 3 | `all_secondary_channels` | 0.018287 | 1.000000 | 0.035917 | 0.024737 |
| 4 | `spray_or_foam` | 0.017504 | 0.884328 | 0.034329 | 0.022853 |
| 5 | `bubble` | 0.017009 | 0.143390 | 0.030411 | 0.003813 |
| 6 | `foam_or_bubble_density_ge_64` | 0.015552 | 0.670043 | 0.030398 | 0.019489 |
| 7 | `spray` | 0.015546 | 0.504264 | 0.030163 | 0.014673 |
| 8 | `foam_density_ge_64` | 0.015315 | 0.540512 | 0.029786 | 0.015965 |

### S401_CR21_union

| Rank | Candidate | Precision | Recall | F1 | Coverage |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `all_secondary_channels_density_ge_8` | 0.054776 | 0.394862 | 0.096206 | 0.046142 |
| 2 | `all_secondary_channels_density_ge_16` | 0.055090 | 0.370527 | 0.095918 | 0.043052 |
| 3 | `spray_density_ge_8` | 0.056556 | 0.305696 | 0.095452 | 0.034599 |
| 4 | `spray_or_foam_density_ge_8` | 0.054824 | 0.366986 | 0.095397 | 0.042847 |
| 5 | `spray_or_foam_density_ge_16` | 0.054872 | 0.343065 | 0.094611 | 0.040019 |
| 6 | `spray_density_ge_16` | 0.056786 | 0.280570 | 0.094455 | 0.031626 |
| 7 | `all_secondary_channels_density_ge_32` | 0.053910 | 0.323778 | 0.092430 | 0.038443 |
| 8 | `spray_or_foam_density_ge_32` | 0.053567 | 0.298614 | 0.090839 | 0.035682 |

### S409_SF12_H18_highlight

| Rank | Candidate | Precision | Recall | F1 | Coverage |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `spray_density_ge_8` | 0.004530 | 0.039263 | 0.008123 | 0.034599 |
| 2 | `all_secondary_channels_density_ge_8` | 0.003930 | 0.045424 | 0.007234 | 0.046142 |
| 3 | `spray_or_foam_density_ge_8` | 0.003658 | 0.039263 | 0.006692 | 0.042847 |
| 4 | `spray_density_ge_16` | 0.003111 | 0.024645 | 0.005524 | 0.031626 |
| 5 | `all_secondary_channels_density_ge_16` | 0.002632 | 0.028390 | 0.004818 | 0.043052 |
| 6 | `spray_or_foam_density_ge_16` | 0.002458 | 0.024645 | 0.004471 | 0.040019 |
| 7 | `bubble_density_ge_8` | 0.002401 | 0.006705 | 0.003536 | 0.011146 |
| 8 | `bubble_density_ge_16` | 0.001590 | 0.003805 | 0.002243 | 0.009553 |

### S409_SF12_H18_channel_band

| Rank | Candidate | Precision | Recall | F1 | Coverage |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `spray` | 0.437650 | 0.794102 | 0.564300 | 0.014673 |
| 2 | `spray_or_foam` | 0.353837 | 1.000000 | 0.522718 | 0.022853 |
| 3 | `all_secondary_channels` | 0.326900 | 1.000000 | 0.492727 | 0.024737 |
| 4 | `spray_density_ge_64` | 0.308750 | 0.822907 | 0.449027 | 0.021553 |
| 5 | `spray_or_foam_density_ge_64` | 0.268499 | 1.000000 | 0.423333 | 0.030117 |
| 6 | `all_secondary_channels_density_ge_64` | 0.249799 | 1.000000 | 0.399743 | 0.032372 |
| 7 | `spray_density_ge_32` | 0.253554 | 0.847686 | 0.390350 | 0.027035 |
| 8 | `spray_or_foam_density_ge_32` | 0.226622 | 1.000000 | 0.369506 | 0.035682 |

### S409_SF12_H18_union

| Rank | Candidate | Precision | Recall | F1 | Coverage |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | `spray` | 0.437650 | 0.531652 | 0.480093 | 0.014673 |
| 2 | `spray_or_foam` | 0.353837 | 0.669502 | 0.462984 | 0.022853 |
| 3 | `all_secondary_channels` | 0.326900 | 0.669502 | 0.439301 | 0.024737 |
| 4 | `spray_density_ge_64` | 0.308750 | 0.550937 | 0.395730 | 0.021553 |
| 5 | `spray_or_foam_density_ge_64` | 0.268499 | 0.669502 | 0.383284 | 0.030117 |
| 6 | `all_secondary_channels_density_ge_64` | 0.249799 | 0.669502 | 0.363843 | 0.032372 |
| 7 | `spray_density_ge_32` | 0.254214 | 0.569004 | 0.351423 | 0.027035 |
| 8 | `spray_or_foam_density_ge_32` | 0.227122 | 0.670979 | 0.339370 | 0.035682 |

## Frame Samples

| Mask | Output | Grid |
| --- | ---: | --- |
| `S401_CR21_highlight` | 0 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_highlight_0000_mask_channel_join.png` |
| `S401_CR21_highlight` | 7 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_highlight_0001_mask_channel_join.png` |
| `S401_CR21_highlight` | 13 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_highlight_0002_mask_channel_join.png` |
| `S401_CR21_highlight` | 20 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_highlight_0003_mask_channel_join.png` |
| `S401_CR21_highlight` | 27 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_highlight_0004_mask_channel_join.png` |
| `S401_CR21_highlight` | 34 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_highlight_0005_mask_channel_join.png` |
| `S401_CR21_highlight` | 40 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_highlight_0006_mask_channel_join.png` |
| `S401_CR21_highlight` | 47 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_highlight_0007_mask_channel_join.png` |
| `S401_CR21_dark_primary` | 0 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_dark_primary_0000_mask_channel_join.png` |
| `S401_CR21_dark_primary` | 7 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_dark_primary_0001_mask_channel_join.png` |
| `S401_CR21_dark_primary` | 13 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_dark_primary_0002_mask_channel_join.png` |
| `S401_CR21_dark_primary` | 20 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_dark_primary_0003_mask_channel_join.png` |
| `S401_CR21_dark_primary` | 27 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_dark_primary_0004_mask_channel_join.png` |
| `S401_CR21_dark_primary` | 34 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_dark_primary_0005_mask_channel_join.png` |
| `S401_CR21_dark_primary` | 40 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_dark_primary_0006_mask_channel_join.png` |
| `S401_CR21_dark_primary` | 47 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_dark_primary_0007_mask_channel_join.png` |
| `S401_CR21_channel_band` | 0 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_channel_band_0000_mask_channel_join.png` |
| `S401_CR21_channel_band` | 7 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_channel_band_0001_mask_channel_join.png` |
| `S401_CR21_channel_band` | 13 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_channel_band_0002_mask_channel_join.png` |
| `S401_CR21_channel_band` | 20 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_channel_band_0003_mask_channel_join.png` |
| `S401_CR21_channel_band` | 27 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_channel_band_0004_mask_channel_join.png` |
| `S401_CR21_channel_band` | 34 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_channel_band_0005_mask_channel_join.png` |
| `S401_CR21_channel_band` | 40 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_channel_band_0006_mask_channel_join.png` |
| `S401_CR21_channel_band` | 47 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_channel_band_0007_mask_channel_join.png` |
| `S401_CR21_union` | 0 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_union_0000_mask_channel_join.png` |
| `S401_CR21_union` | 7 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_union_0001_mask_channel_join.png` |
| `S401_CR21_union` | 13 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_union_0002_mask_channel_join.png` |
| `S401_CR21_union` | 20 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_union_0003_mask_channel_join.png` |
| `S401_CR21_union` | 27 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_union_0004_mask_channel_join.png` |
| `S401_CR21_union` | 34 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_union_0005_mask_channel_join.png` |
| `S401_CR21_union` | 40 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_union_0006_mask_channel_join.png` |
| `S401_CR21_union` | 47 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s401_cr21_union_0007_mask_channel_join.png` |
| `S409_SF12_H18_highlight` | 0 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s409_sf12_h18_highlight_0000_mask_channel_join.png` |
| `S409_SF12_H18_highlight` | 7 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s409_sf12_h18_highlight_0001_mask_channel_join.png` |
| `S409_SF12_H18_highlight` | 13 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s409_sf12_h18_highlight_0002_mask_channel_join.png` |
| `S409_SF12_H18_highlight` | 20 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s409_sf12_h18_highlight_0003_mask_channel_join.png` |
| `S409_SF12_H18_highlight` | 27 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s409_sf12_h18_highlight_0004_mask_channel_join.png` |
| `S409_SF12_H18_highlight` | 34 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s409_sf12_h18_highlight_0005_mask_channel_join.png` |
| `S409_SF12_H18_highlight` | 40 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s409_sf12_h18_highlight_0006_mask_channel_join.png` |
| `S409_SF12_H18_highlight` | 47 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s409_sf12_h18_highlight_0007_mask_channel_join.png` |
| `S409_SF12_H18_channel_band` | 0 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s409_sf12_h18_channel_band_0000_mask_channel_join.png` |
| `S409_SF12_H18_channel_band` | 7 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s409_sf12_h18_channel_band_0001_mask_channel_join.png` |
| `S409_SF12_H18_channel_band` | 13 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s409_sf12_h18_channel_band_0002_mask_channel_join.png` |
| `S409_SF12_H18_channel_band` | 20 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s409_sf12_h18_channel_band_0003_mask_channel_join.png` |
| `S409_SF12_H18_channel_band` | 27 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s409_sf12_h18_channel_band_0004_mask_channel_join.png` |
| `S409_SF12_H18_channel_band` | 34 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s409_sf12_h18_channel_band_0005_mask_channel_join.png` |
| `S409_SF12_H18_channel_band` | 40 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s409_sf12_h18_channel_band_0006_mask_channel_join.png` |
| `S409_SF12_H18_channel_band` | 47 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s409_sf12_h18_channel_band_0007_mask_channel_join.png` |
| `S409_SF12_H18_union` | 0 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s409_sf12_h18_union_0000_mask_channel_join.png` |
| `S409_SF12_H18_union` | 7 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s409_sf12_h18_union_0001_mask_channel_join.png` |
| `S409_SF12_H18_union` | 13 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s409_sf12_h18_union_0002_mask_channel_join.png` |
| `S409_SF12_H18_union` | 20 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s409_sf12_h18_union_0003_mask_channel_join.png` |
| `S409_SF12_H18_union` | 27 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s409_sf12_h18_union_0004_mask_channel_join.png` |
| `S409_SF12_H18_union` | 34 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s409_sf12_h18_union_0005_mask_channel_join.png` |
| `S409_SF12_H18_union` | 40 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s409_sf12_h18_union_0006_mask_channel_join.png` |
| `S409_SF12_H18_union` | 47 | `build/shots/s423_mitsuba_source_response_intent_channel_analysis/grids/s409_sf12_h18_union_0007_mask_channel_join.png` |

## Next

Use high-F1 channel overlaps to drive renderer-native secondary material attenuation; keep highlight masks separate from secondary channels.
