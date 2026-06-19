# S196 S195 Gallery Publish

## Goal

Publish the S195 strong smoothing full-shot candidate so it can be inspected
outside the local workspace before accepting or rejecting it.

## Inputs

- Shot directory: `build/shots/s195_water_mesh_smoothing_strong`
- Shot GIF: `build/shots/s195_water_mesh_smoothing_strong/shot.gif`
- Comparison sheet:
  `build/shots/s195_water_mesh_smoothing_strong/comparison/comparison_sheet.png`
- Comparison summary:
  `build/shots/s195_water_mesh_smoothing_strong/comparison/comparison_summary.json`
- S195 comparison report:
  `docs/reports/cinematic_water_mesh_smoothing_strong_comparison_s195.md`

## Commands

```powershell
python tools\build_bridge_cinematic_gallery.py build\shots\s195_water_mesh_smoothing_strong --out build\shots\s195_water_mesh_smoothing_strong\gallery --comparison-sheet build\shots\s195_water_mesh_smoothing_strong\comparison\comparison_sheet.png --comparison-summary build\shots\s195_water_mesh_smoothing_strong\comparison\comparison_summary.json --comparison-label "S191 vs S195 Comparison" --title "S195 Strong Water Mesh Smoothing" --keyframes 3 --report docs\reports\cinematic_water_mesh_smoothing_strong_gallery_s196.md
```

```powershell
python tools\publish_cinematic_gallery.py build\shots\s195_water_mesh_smoothing_strong\gallery --port 8835 --cftunnel --manifest build\shots\s195_water_mesh_smoothing_strong\gallery_publish_s196_manifest.json --report docs\reports\cinematic_gallery_publish_s196.md --timeout-seconds 180
```

## Result

- Public URL: `https://dicke-automotive-fitness-category.trycloudflare.com`
- Local URL: `http://127.0.0.1:8835`
- HTTP server PID: `96544`
- cloudflared PID: `87180`
- Gallery report:
  `docs/reports/cinematic_water_mesh_smoothing_strong_gallery_s196.md`
- Publish report: `docs/reports/cinematic_gallery_publish_s196.md`

Fresh public checks:

- `https://dicke-automotive-fitness-category.trycloudflare.com/index.html`:
  HTTP `200`
- `https://dicke-automotive-fitness-category.trycloudflare.com/assets/shot.gif`:
  HTTP `200`, `23417683` bytes
- `https://dicke-automotive-fitness-category.trycloudflare.com/assets/comparison.png`:
  HTTP `200`, `2260139` bytes
- `https://dicke-automotive-fitness-category.trycloudflare.com/assets/keyframe_00.png`:
  HTTP `200`, `1131832` bytes

## Next

S197 should triage the public S195 gallery. If the smoother water-body edge
reads better than S191 despite the small contrast loss, accept S195. Otherwise
keep S191 and move the next visual work to reconstruction/export smoothing.
