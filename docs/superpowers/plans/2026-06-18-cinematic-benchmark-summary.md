# Cinematic Benchmark Summary

## Goal

Create a compact benchmark table for recent cinematic gates so runtime, grid size, and key QA metrics can be compared without opening each full report.

## Scope

- Add `tools/summarize_cinematic_gates.py`.
- Read existing `shot_summary.json` files.
- Emit a Markdown report with grid size, frame count, secondary count, visual QA, focus QA, secondary depth, framing, stage timing, and GIF size.
- Generate `docs/reports/cinematic_benchmark_summary_s105.md` from S100, S102, S103, and S104.
- Do not rerun cinematic renders.

## Validation

```powershell
python -m py_compile tools\summarize_cinematic_gates.py
python tools\summarize_cinematic_gates.py build\shots\s100_water_depth_focus_comparison\shot_summary.json build\shots\s102_water_volume_scattering\shot_summary.json build\shots\s103_secondary_render_integration_review\shot_summary.json build\shots\s104_large_grid_cinematic_benchmark\shot_summary.json --out docs\reports\cinematic_benchmark_summary_s105.md
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S105 generated:

- `tools/summarize_cinematic_gates.py`
- `docs/reports/cinematic_benchmark_summary_s105.md`

The report summarizes S100, S102, S103, and S104. The main signal is that the `32 x 40 x 26` gate remains visually valid but costs more:

- S100 total: `443.28s`, render: `198.04s`
- S102 total: `477.18s`, render: `208.26s`
- S103 total: `455.49s`, render: `201.55s`
- S104 total: `693.33s`, render: `281.17s`

S104 keeps visual/focus/depth gates passing, but its framing metric captures the expected wider-grid tradeoff: mean inside ratio `0.976`, while the first frame inside ratio drops to `0.145`.

## Next

S106 should use this summary to choose a narrow larger-grid render-quality follow-up, rather than adding another broad visual pass blindly.
