# S146 S145 Gallery Refresh Publish

## Objective

Package and publish the S145 foreground surface-detail/foam-breakup Blender review so the current shot can be inspected externally before selecting the next visible adjustment.

## Inputs

- Shot output: `build/shots/s145_foreground_surface_detail_foam`
- Shot report: `docs/reports/cinematic_foreground_surface_detail_foam_s145.md`
- Shot GIF: `build/shots/s145_foreground_surface_detail_foam/shot.gif`
- Review manifest: `build/shots/s145_foreground_surface_detail_foam/review/review_manifest.json`

## Scope

- Build an artifact package report for the S145 GIF and review sheets.
- Build a self-contained static gallery under the S145 shot directory.
- Publish the gallery with a Cloudflare quick tunnel.
- Verify local and public `index.html` plus `assets/shot.gif`.

## Non-Goals

- Do not re-render the S145 shot unless the existing artifacts fail validation.
- Do not stop existing public gallery tunnels.
- Do not select the next look-dev adjustment until the S145 gallery is verified.

## Commands

```powershell
python tools\package_cinematic_artifacts.py build\shots\s145_foreground_surface_detail_foam --out docs\reports\cinematic_artifact_package_s146.md
python tools\build_cinematic_gallery.py build\shots\s145_foreground_surface_detail_foam --package docs\reports\cinematic_artifact_package_s146.md --out build\shots\s145_foreground_surface_detail_foam\gallery --report docs\reports\cinematic_static_gallery_s146.md
python tools\publish_cinematic_gallery.py build\shots\s145_foreground_surface_detail_foam\gallery --port 8803 --cftunnel --manifest build\shots\s145_foreground_surface_detail_foam\gallery\publish_manifest_s146.json --report docs\reports\cinematic_gallery_publish_s146.md --timeout-seconds 120
```

## Acceptance Gate

- Artifact package report exists and marks required assets present.
- Static gallery has `index.html`, `gallery_manifest.json`, and copied review assets.
- Publish manifest records a local URL and a public Cloudflare URL.
- Local and public `index.html` return HTTP 200.
- Local and public `assets/shot.gif` return HTTP 200 and nonzero bytes.

## Verification

```powershell
git diff --check
```
