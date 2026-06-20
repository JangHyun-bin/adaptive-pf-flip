# S479 Mitsuba Response Control Handoff

Generated UTC: `2026-06-20T16:36:54.996976+00:00`
Status: `ready`
Handoff JSON: `build/shots/s479_mitsuba_response_control_handoff/response_control_handoff.json`
Light contract: `build/shots/s479_mitsuba_response_control_handoff/light_response_contract.json`
Material contract: `build/shots/s479_mitsuba_response_control_handoff/material_response_contract.json`
Gallery: `build/shots/s479_mitsuba_response_control_handoff/gallery/index.html`

## Scope

S479 packages the promoted S478 `p4_soft_wide` response-control proxy into renderer-facing contracts.
The light contract is schema-compatible with the existing Mitsuba XML light consumer; the material contract carries the remaining water material/volume controls for the next native pass.

## Checks

- Controls: `10`
- Light controls: `8`
- Material controls: `2`
- Light frames: `5`
- Material frames: `2`
- Promoted proxy frames: `8`
- Promoted proxy controls applied: `10`
- Promoted mean target-gap MAD: `19.079715470679012`
- Promoted max target-gap MAD: `23.9488554526749`
- Promoted max abs gap: `176`
- Baseline mean target-gap MAD: `19.10240579989712`
- Baseline max target-gap MAD: `23.950307355967077`
- Mean MAD improvement vs baseline: `0.022690329218107763`
- Max MAD improvement vs baseline: `0.0014519032921782582`

## Outputs

| Artifact | Schema | Status | Path |
| --- | --- | --- | --- |
| Handoff | `lsfs_mitsuba_response_control_handoff` | `ready` | `build/shots/s479_mitsuba_response_control_handoff/response_control_handoff.json` |
| Light contract | `lsfs_mitsuba_light_response_contract` | `ready` | `build/shots/s479_mitsuba_response_control_handoff/light_response_contract.json` |
| Material contract | `lsfs_mitsuba_material_response_contract` | `ready` | `build/shots/s479_mitsuba_response_control_handoff/material_response_contract.json` |

## Gallery Assets

| Asset | Size | Path |
| --- | ---: | --- |
| Promoted Proxy GIF | 5.80 MB | `build/shots/s479_mitsuba_response_control_handoff/gallery/assets/promoted_proxy.gif` |
| Response Control Overlay GIF | 943.06 KB | `build/shots/s479_mitsuba_response_control_handoff/gallery/assets/response_controls.gif` |
| Promoted Proxy Target Gap GIF | 8.20 MB | `build/shots/s479_mitsuba_response_control_handoff/gallery/assets/promoted_proxy_target_gap.gif` |
| Promoted Proxy Gap Strip | 1.71 MB | `build/shots/s479_mitsuba_response_control_handoff/gallery/assets/promoted_proxy_gap_strip_03.png` |

## Next

Consume the light contract in the Mitsuba XML path, then add the material contract consumer and compare the native render against the promoted proxy gate.
