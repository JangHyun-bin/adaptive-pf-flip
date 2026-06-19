# S194 Smoothing Occlusion Probe Matrix

## Status

Passed.

## Artifacts

- Matrix sheet: `build\shots\s194_smoothing_occlusion_probe_matrix\probe_matrix.png`

## Candidate Metrics

| Candidate | Preset | Min contrast | Mean luminance | Bright ratio | Highlight ratio | Nonblank | Mean diff | Changed ratio |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| S191 | `dam_break_water_mesh_smoothing` | 174.0 | 81.84205240885416 | 0.0001904296875 | 0.0001220703125 | 1.0 | None | None |
| soft | `dam_break_water_mesh_smoothing_soft_probe` | 148.0 | 81.84995768229166 | 0.00017198350694444444 | 0.0001150173611111111 | 1.0 | 0.8648383246527778 | 0.0014463975694444444 |
| strong | `dam_break_water_mesh_smoothing_strong_probe` | 184.0 | 81.82086859809027 | 0.00021375868055555555 | 0.00013943142361111111 | 1.0 | 0.8927864583333334 | 0.002041015625 |
| occlusion | `dam_break_water_volume_occlusion_probe` | 183.0 | 74.52631022135417 | 0.00016221788194444446 | 0.00010470920138888889 | 1.0 | 7.654308810763888 | 0.499453125 |

## Candidate Passes

### S191

- Smoothing: `{'enabled': True, 'factor': 0.075, 'iterations': 2, 'shade_smooth': True}`
- Volume occlusion: `{}`

### soft

- Smoothing: `{'enabled': True, 'factor': 0.045, 'iterations': 1, 'shade_smooth': True}`
- Volume occlusion: `{'alpha_scale': 1.0, 'emission_scale': 0.0, 'enabled': False, 'inset': 0.15, 'layers': 0, 'region_max': [27.0, 8.4, 19.0], 'region_min': [1.0, 2.4, 3.2]}`

### strong

- Smoothing: `{'enabled': True, 'factor': 0.12, 'iterations': 3, 'shade_smooth': True}`
- Volume occlusion: `{'alpha_scale': 1.0, 'emission_scale': 0.0, 'enabled': False, 'inset': 0.15, 'layers': 0, 'region_max': [27.0, 8.4, 19.0], 'region_min': [1.0, 2.4, 3.2]}`

### occlusion

- Smoothing: `{'enabled': True, 'factor': 0.075, 'iterations': 2, 'shade_smooth': True}`
- Volume occlusion: `{'alpha_scale': 1.0, 'emission_scale': 0.0, 'enabled': True, 'inset': 0.85, 'layers': 5, 'region_max': [34.2, 8.9, 24.5], 'region_min': [1.0, 1.2, 2.8]}`

## Next

Select `dam_break_water_mesh_smoothing_strong_probe` for the next full-shot
render. It keeps nonblank coverage at 1.0, raises minimum contrast from 174 to
184, and limits the selected-frame diff to a small localized water-body change.

Do not promote `dam_break_water_volume_occlusion_probe` yet. It keeps nonblank
coverage and contrast, but mean luminance drops from 81.84 to 74.53 and the
selected-frame changed ratio rises to 0.499, which is too broad for a bounded
depth cue.
