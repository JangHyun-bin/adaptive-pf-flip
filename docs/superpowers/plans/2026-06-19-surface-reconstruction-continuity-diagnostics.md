# S189 Surface Reconstruction Continuity Diagnostics

Date: 2026-06-19

## Goal

Measure the remaining structural water-surface artifacts before adding another
render-look preset.

## Scope

- Add a diagnostic tool that reads an existing Blender `bridge_summary.json`.
- Generate per-frame CSV and JSON diagnostics without rerunning simulation.
- Produce a Markdown report with trend summaries and worst continuity frames.
- Use S186 as the accepted current look.

## Implementation

- `tools/analyze_surface_continuity.py`
  - Extracts water mesh face/vertex counts, water depth spans, secondary totals,
    contact foam counts, and impact ripple counts.
  - Computes per-frame deltas and a bounded continuity risk score.
  - Emits missing occupied-cell counts as a warning rather than failing, because
    S186 bridge summaries do not currently carry that field.
- `docs/reports/cinematic_surface_continuity_diagnostics_s189.md`
  - Records trend summaries, worst frames, sanity checks, and next
    recommendation.

## Command

```powershell
python tools\analyze_surface_continuity.py build\shots\s186_water_surface_continuity_stabilized\blender\bridge_summary.json --out-dir build\shots\s189_surface_continuity_diagnostics --report docs\reports\cinematic_surface_continuity_diagnostics_s189.md
```

## Result

S189 passed:

- Frames: `36`
- Worst continuity frame: `27`
- Max continuity risk score: `0.6886864636676736`
- Water mesh face count delta: `4060`
- Water mesh vertex count delta: `2030`
- Water depth Y-span delta: `-6`
- Water depth Z-span delta: `5`
- Water depth aspect delta: `1.0555555555555558`
- Secondary total count delta: `708`

## Follow-Up

S190 should strengthen the reconstruction/export metric path before the next
look change:

- Carry occupied-cell counts into the bridge summary when available.
- Add continuity diagnostics to the exported render-data summary or a companion
  report.
- Use measured worst frames to decide between mesh smoothing, reconstruction
  export changes, or renderer-side water-volume occlusion.
