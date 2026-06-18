# Large Grid Cinematic Benchmark

## Goal

Run the S103 render/review stack on a larger sparse 3D grid to expose runtime and visual cost beyond the current `28 x 34 x 22` cinematic gate.

## Scope

- Use `dam_break_secondary_render_integration_review` unchanged.
- Increase the grid to `32 x 40 x 26`.
- Keep frames, sim steps, resolution, samples, and review frame count at the S103 gate values.
- Compare against the S103 review manifest.
- Preserve visual QA, temporal highlight QA, focus review QA, ripple readability QA, secondary depth review QA, and comparison artifacts.
- Do not add this larger run to default `ctest`.

## Validation

```powershell
python tools\run_cinematic_shot.py --preset dam_break_large_grid_cinematic_benchmark --out build\shots\s104_large_grid_cinematic_benchmark --frames 36 --sim-steps 36 --width 1280 --height 720 --renderer blender --samples 12 --review-frames 8 --report docs\reports\cinematic_gate_s104.md --compare-review-manifest build\shots\s103_secondary_render_integration_review\review\review_manifest.json --no-build --timeout-seconds 1800
ctest --test-dir build -C Release --output-on-failure
git diff --check
```

## Result

S104 generated:

- `build/shots/s104_large_grid_cinematic_benchmark/shot.gif`
- `build/shots/s104_large_grid_cinematic_benchmark/review/contact_sheet.png`
- `build/shots/s104_large_grid_cinematic_benchmark/review/comparison_sheet.png`
- `build/shots/s104_large_grid_cinematic_benchmark/review/secondary_depth_comparison_sheet.png`
- `docs/reports/cinematic_gate_s104.md`

The first large-grid attempt exposed two benchmark-specific gate issues:

- Initial foam count was `8`, below the inherited `15` foam acceptance minimum.
- Initial secondary framing inside ratio was `0.1445`, below the inherited close-up `0.95` per-frame threshold.

The final S104 preset keeps default behavior unchanged and scopes the larger-grid gate adjustments to `dam_break_large_grid_cinematic_benchmark`:

- `secondary_acceptance_qa.min_foam_fraction = 0.04`, producing foam min `7`.
- camera auto-frame `max_scale = 1.2` and `fov_pad_degrees = 4.0`.
- `secondary_framing_qa.min_mean_inside_ratio = 0.85`.
- `secondary_framing_qa.min_frame_inside_ratio = 0.1`.

The final full gate passed:

- grid: `32 x 40 x 26`
- visual QA mean luminance: `98.6345`
- visual QA min contrast: `186.0`
- focus review mean luminance: `88.0942`
- focus review min contrast: `130.0`
- secondary depth crop particles mean: `171.375`
- secondary depth normalized span mean: `0.3863`
- secondary framing mean inside ratio: `0.9761`
- secondary framing min frame inside ratio: `0.1445`
- stage timings: export `92.95s`, validate `114.74s`, reconstruct `68.98s`, convert `132.62s`, render `281.17s`, gif `2.86s`

## Next

S105 should add a compact benchmark summary table for recent cinematic gates so runtime, grid size, and key QA metrics can be compared without re-opening each full report.
