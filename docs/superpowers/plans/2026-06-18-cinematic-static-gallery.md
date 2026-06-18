# S121 Cinematic Static Gallery

## Objective

Turn the S120 Markdown package into a self-contained browser gallery that can be served locally or through a tunnel without depending on parent shot-directory paths.

## Command

```powershell
python tools\build_cinematic_gallery.py build\shots\s119_blender_quality_baseline_comparison --package docs\reports\cinematic_artifact_package_s120.md --out build\shots\s119_blender_quality_baseline_comparison\gallery --report docs\reports\cinematic_static_gallery_s121.md
```

## Result

S121 passed and produced:

- `build/shots/s119_blender_quality_baseline_comparison/gallery/index.html`
- `build/shots/s119_blender_quality_baseline_comparison/gallery/gallery_manifest.json`
- `build/shots/s119_blender_quality_baseline_comparison/gallery/assets/shot.gif`
- `docs/reports/cinematic_static_gallery_s121.md`

The gallery copies 12 review artifacts plus `shot_summary.json` and the S120 artifact package into the gallery directory.

## Verification

```powershell
python -m py_compile tools\build_cinematic_gallery.py tools\package_cinematic_artifacts.py
python tools\build_cinematic_gallery.py build\shots\s119_blender_quality_baseline_comparison --package docs\reports\cinematic_artifact_package_s120.md --out build\shots\s119_blender_quality_baseline_comparison\gallery --report docs\reports\cinematic_static_gallery_s121.md
python -m http.server 8898 --bind 127.0.0.1 --directory build\shots\s119_blender_quality_baseline_comparison\gallery
```

HTTP verification returned:

- `index.html`: 200, 8161 bytes
- `assets/shot.gif`: 200, 25268927 bytes

## Next

S122 should expose this gallery through a short-lived cftunnel and verify the HTML plus copied assets over HTTP.
