# S204 Component Material Overlay

## Status

Passed.

## Artifacts

- Overlay sheet: `build\shots\s204_component_material_probe\overlay\component_overlay_sheet.png`
- Overlay frames: `8`

## Summary

- Filter threshold: `0.24`
- Component rows: `15`
- Would-filter components: `7`
- Visible would-filter components: `7`

## Finding

The same component that would be removed by the S200/S202 pruning threshold is
still visible in this S204 treated render window. S204 therefore treats the
component as meaningful water: it keeps the geometry and only assigns the
smaller connected component a softer material.

## Components

| Render frame | Mesh frame | Component | Face ratio | Would filter | Inside ratio |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 0 | 1 | 0.767793 | `False` | 0.9641470359823971 |
| 0 | 0 | 2 | 0.232207 | `True` | 0.28999144568006846 |
| 1 | 1 | 1 | 0.777375 | `False` | 0.9592285788247477 |
| 1 | 1 | 2 | 0.222625 | `True` | 0.34146341463414637 |
| 2 | 1 | 1 | 0.777375 | `False` | 0.9434377426870308 |
| 2 | 1 | 2 | 0.222625 | `True` | 0.32429990966576333 |
| 3 | 2 | 1 | 0.774258 | `False` | 0.9158684959875745 |
| 3 | 2 | 2 | 0.225742 | `True` | 0.30479148181011534 |
| 4 | 3 | 1 | 0.772246 | `False` | 0.8886875485374062 |
| 4 | 3 | 2 | 0.227754 | `True` | 0.32280701754385965 |
| 5 | 4 | 1 | 0.774413 | `False` | 0.8679782552420399 |
| 5 | 4 | 2 | 0.225587 | `True` | 0.3401420959147424 |
| 6 | 4 | 1 | 0.774413 | `False` | 0.8547760807662439 |
| 6 | 4 | 2 | 0.225587 | `True` | 0.3077264653641208 |
| 7 | 5 | 1 | 1 | `False` | 0.7308 |

## Next

Do not enable face-ratio pruning for the cinematic baseline. If component-aware
treatment is revisited, test it as a material/attribute pass, not as a deletion
rule.
