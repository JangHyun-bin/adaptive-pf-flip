# S495 Mitsuba Low Frequency Runtime Import Preview

Generated UTC: `2026-06-20T18:24:26.242130+00:00`
Preview JSON: `build/shots/s495_mitsuba_low_frequency_runtime_import_preview/runtime_import_preview.json`
Index HTML: `build/shots/s495_mitsuba_low_frequency_runtime_import_preview/index.html`
Status: `ready`
Source bundle: `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/runtime_handoff_bundle.json`

## Checks

- Frames: `8`
- Ready frames: `8`
- Missing required bindings: `0`
- Hash mismatches: `0`
- Size mismatches: `0`
- Dimension mismatches: `0`
- Bundle-local violations: `0`
- Source dependency leaks: `0`
- Proof failures: `0`

## Runtime Assets

| Asset | Role | Size | Path |
| --- | --- | ---: | --- |
| runtime_webgl | `runtime` | 9.10 KB | `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/runtime/runtime_webgl.html` |
| webgl_proof_gif | `proof_gallery` | 4.21 MB | `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/gallery/webgl_proof.gif` |
| low_frequency_parity_post_tonemap.glsl | `glsl_shader` | 705 B | `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/shaders/low_frequency_parity_post_tonemap.glsl` |
| low_frequency_parity_post_tonemap.hlsl | `hlsl_shader` | 859 B | `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/shaders/low_frequency_parity_post_tonemap.hlsl` |

## Frame Imports

| Frame | Ready | Inputs | Oracle | WebGL |
| ---: | --- | ---: | --- | --- |
| 0 | `True` | 3 | `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/oracle/frame_0000_oracle.png` | `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0000/proof/frame_0000_webgl_frame.png` |
| 1 | `True` | 3 | `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/oracle/frame_0001_oracle.png` | `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0001/proof/frame_0001_webgl_frame.png` |
| 2 | `True` | 3 | `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/oracle/frame_0002_oracle.png` | `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0002/proof/frame_0002_webgl_frame.png` |
| 3 | `True` | 3 | `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/oracle/frame_0003_oracle.png` | `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0003/proof/frame_0003_webgl_frame.png` |
| 4 | `True` | 3 | `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/oracle/frame_0004_oracle.png` | `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0004/proof/frame_0004_webgl_frame.png` |
| 5 | `True` | 3 | `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/oracle/frame_0005_oracle.png` | `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0005/proof/frame_0005_webgl_frame.png` |
| 6 | `True` | 3 | `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/oracle/frame_0006_oracle.png` | `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0006/proof/frame_0006_webgl_frame.png` |
| 7 | `True` | 3 | `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/oracle/frame_0007_oracle.png` | `build/shots/s494_mitsuba_low_frequency_runtime_handoff_bundle/frames/frame_0007/proof/frame_0007_webgl_frame.png` |

## Next

Use this bundle-only import preview as the gate before wiring the production renderer UI/export path.
