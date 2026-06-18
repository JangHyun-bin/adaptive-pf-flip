# Cinematic Visual QA Metrics

## Goal

Make cinematic gates fail on obviously weak rendered output before manual review.

## Scope

- Extend Blender bridge image stats with mean luminance, bright-pixel ratio, highlight ratio, dark ratio, and aggregate visual QA summary.
- Add preset-driven visual QA thresholds to the cinematic runner.
- Record visual QA summary and pass/fail checks in `shot_summary.json` and the Markdown report.
- Keep the gate opt-in through the render preset so non-Blender or early smoke paths are not forced into the same thresholds.

## Validation

```powershell
python -m json.tool configs\cinematic_presets.json > $null
python -m py_compile tools\run_cinematic_shot.py tools\render_bridge_blender.py
python tools\run_cinematic_shot.py --preset dam_break_contact_closeup --out build\shots\s65_visual_qa_metrics --nx 28 --ny 34 --nz 22 --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s65.md --compare-review-manifest build\shots\s62_secondary_size_pass\review\review_manifest.json --no-build --timeout-seconds 1500
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S65 generated:

- `build/shots/s65_visual_qa_metrics/shot.gif`
- `build/shots/s65_visual_qa_metrics/review/contact_sheet.png`
- `build/shots/s65_visual_qa_metrics/review/comparison_sheet.png`
- `docs/reports/cinematic_gate_s65.md`

The visual QA gate passed with nonblank frames, sufficient contrast, bounded mean luminance, and a nonzero bright-pixel ratio.

## Next

S66 should make the secondary channels look less like isolated spheres by adding a volumetric spray/foam render pass or stronger sprite-style secondary shading, while preserving the S65 visual QA gates.
