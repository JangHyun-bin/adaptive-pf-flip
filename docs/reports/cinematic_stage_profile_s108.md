# Cinematic Stage Profile

Generated UTC: `2026-06-18T17:32:00Z`
Source summary: `docs/reports/cinematic_benchmark_summary_s107.md`

## Gate Cost Split

| Gate | Grid | Total | Non-render | Non-render % | Render | Render % | Top non-render |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `dam_break_water_depth_focus_comparison` | `28x34x22` | 443.28s | 242.39s | 54.7% | 198.04s | 44.7% | `Convert` |
| `dam_break_water_volume_scattering` | `28x34x22` | 477.18s | 264.96s | 55.5% | 208.26s | 43.6% | `Convert` |
| `dam_break_secondary_render_integration_review` | `28x34x22` | 455.49s | 251.12s | 55.1% | 201.55s | 44.2% | `Convert` |
| `dam_break_large_grid_cinematic_benchmark` | `32x40x26` | 693.33s | 409.29s | 59.0% | 281.17s | 40.6% | `Convert` |
| `dam_break_large_grid_render_quality_followup` | `32x40x26` | 693.47s | 408.67s | 58.9% | 281.93s | 40.7% | `Convert` |

## Average Stage Breakdown

| Group | Count | Export | Validate | Reconstruct | Convert | Render | Total | Non-render % |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| all gates | 5 | 75.12s | 85.01s | 54.53s | 100.62s | 234.19s | 552.55s | 57.1% |
| large grid | 2 | 92.33s | 114.31s | 69.66s | 132.68s | 281.55s | 693.40s | 59.0% |

## Bottleneck Ranking

| Stage | Average | Share of total |
| --- | ---: | ---: |
| `Render` | 281.55s | 40.6% |
| `Convert` | 132.68s | 19.1% |
| `Validate` | 114.31s | 16.5% |
| `Export` | 92.33s | 13.3% |
| `Reconstruct` | 69.66s | 10.0% |

## S108 Recommendation

- Large-grid non-render work is `408.67s` (58.9%) versus render `281.93s` (40.7%).
- The largest large-grid non-render stage is `Convert`.
- Target cache conversion and cache validation before running another larger-grid cinematic gate.
- Preserve the S106 render preset as the current quality baseline while optimizing the cache path.
