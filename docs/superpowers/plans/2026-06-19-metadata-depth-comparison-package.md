# S174 Metadata Depth Comparison Package

## Objective

Package and compare the S173 metadata-depth attenuation render against the S168
baseline without rerunning simulation.

## Inputs

- Baseline shot: `build/shots/s168_water_depth_foreground_separation`
- Candidate shot: `build/shots/s173_metadata_depth_attenuation`
- Baseline bridge summary:
  `build/shots/s168_water_depth_foreground_separation/blender/bridge_summary.json`
- Candidate bridge summary:
  `build/shots/s173_metadata_depth_attenuation/blender/bridge_summary.json`
- Baseline frames:
  `build/shots/s168_water_depth_foreground_separation/blender/frames`
- Candidate frames:
  `build/shots/s173_metadata_depth_attenuation/blender/frames`

## Scope

- Produce a side-by-side comparison artifact for representative frames.
- Record metric deltas between S168 and S173:
  - mean luminance,
  - bright/highlight ratio,
  - contrast,
  - metadata attenuation factor ranges,
  - secondary count/cap relationship.
- Keep the comparison independent from simulation and cache generation.
- Optionally publish a static gallery after the local comparison is reviewed.

## Non-Goals

- Do not rerun simulation.
- Do not change S173 visual settings in this packaging pass.
- Do not introduce a slow default test.

## Candidate Implementation

Add a lightweight tool, tentatively:

```powershell
python tools\compare_cinematic_frames.py --left build\shots\s168_water_depth_foreground_separation\blender\frames --right build\shots\s173_metadata_depth_attenuation\blender\frames --left-label S168 --right-label S173 --out-dir build\shots\s174_metadata_depth_comparison --summary-left build\shots\s168_water_depth_foreground_separation\blender\bridge_summary.json --summary-right build\shots\s173_metadata_depth_attenuation\blender\bridge_summary.json --report docs\reports\cinematic_metadata_depth_comparison_s174.md
```

## Acceptance Gate

- A comparison sheet or HTML artifact exists under `build/shots/s174_metadata_depth_comparison`.
- Report records S168 vs S173 metric deltas and inspected visual findings.
- `python -m py_compile` passes for any new tool.
- `git diff --check` passes.

## Next Recommendation

If S173 improves depth/secondary read without flattening the surface, move to a
public gallery/package refresh. If the comparison shows over-attenuation, tune
the S173 multiplier bounds before publishing.

## Result

S174 added `tools/compare_cinematic_frames.py` and generated an S168/S173
comparison without rerunning simulation.

Generated artifacts:

- Report: `docs/reports/cinematic_metadata_depth_comparison_s174.md`
- Comparison sheet: `build/shots/s174_metadata_depth_comparison/comparison_sheet.png`
- Comparison summary: `build/shots/s174_metadata_depth_comparison/comparison_summary.json`

Metric deltas:

- Mean luminance delta: `-2.1279213686342615`
- Minimum contrast delta: `1.0`
- Mean bright ratio delta: `-0.0002721113040123457`
- Mean highlight ratio delta: `-0.000015944492669753106`
- Mean nonblank ratio delta: `0.0`

Finding:

- S173 preserves water-surface readability while lowering late-frame secondary
  density and highlight pressure.

Next:

- S175 should package/publish the S173 comparison gallery so the current visual
  state is externally inspectable before the next render tuning pass.
