# Larger External Renderer: Mitsuba AOV Attenuation

Status: complete

## Goal

Use S406 channel evidence to test a bounded target-free local attenuation pass
instead of another broad material or screen-card sweep.

## Scope

- Add channel selection to source-response channel-band masks.
- Preserve CR21 profile parity.
- Generate all-channel and spray/foam attenuation candidates.
- Compare against SS1 and CR21.
- Publish the comparison gallery.

## Result

`SF18_SprayFoam` improves over SS1:

- SS1 max target MAD: `23.951853137860084`
- SF18 max target MAD: `23.77382137345679`
- CR21 max target MAD: `23.552905092592592`

## Decision

Promote `SF18_SprayFoam` as the next AOV attenuation probe. It is not yet the
final visual baseline, but it is a better direction than screen-space cards or
broad secondary material sweeps.

## Next

S408 should tune SF18 locally and keep source-highlight work separate from
secondary-channel attenuation.
