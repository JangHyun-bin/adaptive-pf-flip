# S192 S191 Gallery Publish

Date: 2026-06-19

## Goal

Package and publish the S191 water mesh smoothing render so it can be reviewed
through a public Cloudflare quick tunnel URL.

## Inputs

- Shot directory: `build/shots/s191_water_mesh_smoothing`
- Comparison sheet:
  `build/shots/s191_water_mesh_smoothing/comparison/comparison_sheet.png`
- Comparison summary:
  `build/shots/s191_water_mesh_smoothing/comparison/comparison_summary.json`
- S191 gate report: `docs/reports/cinematic_water_mesh_smoothing_s191.md`

## Commands

```powershell
python tools\build_bridge_cinematic_gallery.py build\shots\s191_water_mesh_smoothing --out build\shots\s191_water_mesh_smoothing\gallery --comparison-sheet build\shots\s191_water_mesh_smoothing\comparison\comparison_sheet.png --comparison-summary build\shots\s191_water_mesh_smoothing\comparison\comparison_summary.json --comparison-label "S186 vs S191 Comparison" --title "S191 Water Mesh Smoothing" --keyframes 3 --report docs\reports\cinematic_water_mesh_smoothing_gallery_s192.md
```

```powershell
python tools\publish_cinematic_gallery.py build\shots\s191_water_mesh_smoothing\gallery --port 8827 --cftunnel --manifest build\shots\s191_water_mesh_smoothing\gallery_publish_s192_manifest.json --report docs\reports\cinematic_gallery_publish_s192.md --timeout-seconds 120
```

## Result

- Public URL: `https://emacs-bases-teens-health.trycloudflare.com`
- Local URL: `http://127.0.0.1:8827`
- HTTP server PID: `125076`
- cloudflared PID: `107140`
- Gallery report: `docs/reports/cinematic_water_mesh_smoothing_gallery_s192.md`
- Publish report: `docs/reports/cinematic_gallery_publish_s192.md`

Fresh public checks:

- `https://emacs-bases-teens-health.trycloudflare.com/index.html`: HTTP `200`,
  `5495` bytes
- `https://emacs-bases-teens-health.trycloudflare.com/assets/shot.gif`: HTTP
  `200`, `23392399` bytes
- `https://emacs-bases-teens-health.trycloudflare.com/assets/comparison.png`:
  HTTP `200`, `2373182` bytes
- `https://emacs-bases-teens-health.trycloudflare.com/assets/keyframe_00.png`:
  HTTP `200`, `1129739` bytes

## Next

S193 should triage the public S191 gallery and decide whether to accept the
mesh smoothing pass or reduce smoothing strength.
