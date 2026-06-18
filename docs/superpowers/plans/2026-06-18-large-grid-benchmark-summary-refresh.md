# Large Grid Benchmark Summary Refresh

## Goal

Refresh the compact cinematic benchmark table with S106 included, and make the table expose the early-frame secondary framing issue that S106 was designed to improve.

## Scope

- Include S100, S102, S103, S104, and S106 shot summaries.
- Add `Framing min` to the summary table so early secondary clipping is visible.
- Add validate, reconstruct, and convert stage timings so non-render cost is visible.
- Keep this as a report/tooling step; do not run a new long render.

## Command

```powershell
python tools\summarize_cinematic_gates.py build\shots\s100_water_depth_focus_comparison\shot_summary.json build\shots\s102_water_volume_scattering\shot_summary.json build\shots\s103_secondary_render_integration_review\shot_summary.json build\shots\s104_large_grid_cinematic_benchmark\shot_summary.json build\shots\s106_large_grid_render_quality_followup\shot_summary.json --out docs\reports\cinematic_benchmark_summary_s107.md
```

## Result

S107 produced `docs/reports/cinematic_benchmark_summary_s107.md`.

- S104 large-grid benchmark: total `693.33s`, render `281.17s`, framing min `0.145`.
- S106 render-quality followup: total `693.47s`, render `281.93s`, framing min `0.387`.
- S106 preserves the large-grid runtime profile while improving the early secondary framing gate.
- Large-grid non-render stages remain expensive: S106 export `91.71s`, validate `113.89s`, reconstruct `70.34s`, convert `132.73s`.

## Next

S108 should target cache/export/validation/conversion performance because the S107 table shows the S106 visual improvement did not change the large-grid runtime profile.
