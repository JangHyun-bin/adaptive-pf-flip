# Cinematic Review Artifact Pack

## Goal

Package each cinematic shot into a compact visual-review bundle: GIF, contact sheet, keyframe thumbnails, generated report, summary JSON, and a manifest tying those artifacts together.

## Scope

- Keep the existing simulation and rendering path unchanged.
- Generate review artifacts after GIF assembly so the pack uses the exact rendered frames.
- Store generated assets under the shot output directory, not in the repository.
- Check in only the runner support, docs, and the S51 generated report.

## Implementation

- Add `--review-frames` and `--no-review-pack` to `tools/run_cinematic_shot.py`.
- Default review pack output:
  - `review/contact_sheet.png`
  - `review/keyframes/*.png`
  - `review/review_manifest.json`
- Record review artifact paths in `shot_summary.json`.
- Include review artifact paths and keyframe count in generated markdown reports.

## Validation

```powershell
python -m py_compile tools\run_cinematic_shot.py
python tools\run_cinematic_shot.py --preset dam_break_cinematic --out build\shots\s51_review_pack --frames 24 --sim-steps 24 --width 640 --height 360 --renderer blender --samples 8 --review-frames 6 --report docs\reports\cinematic_gate_s51.md --no-build
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Next

S52 should run a larger visual gate through the current cinematic stack and compare artifact size, render time, and visible quality against S45-S51.
