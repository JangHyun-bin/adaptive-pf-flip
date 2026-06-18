# Cinematic Cache Export Performance Pass

## Goal

Turn the S107 benchmark table into a concrete next optimization target before running another expensive large-grid cinematic render.

## Scope

- Add `tools/profile_cinematic_stages.py`.
- Read `docs/reports/cinematic_benchmark_summary_s107.md`.
- Produce `docs/reports/cinematic_stage_profile_s108.md`.
- Report per-gate render versus non-render cost.
- Rank large-grid stage bottlenecks.
- Keep this as a report/tooling step; do not change simulation or render output.

## Command

```powershell
python tools\profile_cinematic_stages.py docs\reports\cinematic_benchmark_summary_s107.md --out docs\reports\cinematic_stage_profile_s108.md
```

## Result

S108 produced `docs/reports/cinematic_stage_profile_s108.md`.

- S106 large-grid total: `693.47s`.
- S106 render: `281.93s` (`40.7%`).
- S106 non-render work: `408.67s` (`58.9%`).
- Large-grid average stage ranking: render `281.55s`, convert `132.68s`, validate `114.31s`, export `92.33s`, reconstruct `69.66s`.
- The next optimization should target conversion and validation before another larger-grid cinematic gate.

## Next

S109 should add a conservative converted-sequence reuse/freshness path so repeated cinematic review runs can skip `convert_render_cache` when the manifest, water reconstruction, and converter inputs are unchanged.
