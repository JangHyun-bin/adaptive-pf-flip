# S120 Blender Artifact Inspection Package

## Objective

Package the current S119 Blender quality comparison output into a compact Markdown report that can be opened quickly for visual inspection.

## Command

```powershell
python tools\package_cinematic_artifacts.py build\shots\s119_blender_quality_baseline_comparison --out docs\reports\cinematic_artifact_package_s120.md
```

## Result

S120 passed and produced `docs/reports/cinematic_artifact_package_s120.md`.

The package validates and links:

- `shot.gif`
- `review/contact_sheet.png`
- `review/comparison_sheet.png`
- `review/focus_comparison_sheet.png`
- `review/secondary_depth_comparison_sheet.png`
- `review/ripple_readability_comparison_sheet.png`

It also includes optional diagnostic sheets, render/review metadata links, artifact sizes, image dimensions, shot summary metrics, and inline Markdown previews.

## Verification

```powershell
python -m py_compile tools\package_cinematic_artifacts.py
python tools\package_cinematic_artifacts.py build\shots\s119_blender_quality_baseline_comparison --out docs\reports\cinematic_artifact_package_s120.md
git diff --check
ctest --test-dir build -C Release --output-on-failure
```

## Next

S121 should turn this package into a browser-ready static gallery for local review or cftunnel sharing.
