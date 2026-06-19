# S318 Mitsuba XML Preview Tuned Proof Package

## Goal

Package the current non-Blender XML preview proof chain into a durable handoff
bundle.

## Scope

- Package the S316 tuned preview gallery assets.
- Include the S316 preview summary.
- Attach summary sources for:
  - S312 Mitsuba phase-proxy XML export
  - S313 Mitsuba XML validation
  - S316 tuned preview summary
  - S317 tuned preview publish manifest
  - S306 Blender full48 publish manifest
- Write a Markdown package report.

## Result

- Package JSON:
  `build/shots/s318_mitsuba_xml_preview_tuned_proof_package/review_package.json`
- Report:
  `docs/reports/cinematic_mitsuba_xml_preview_tuned_proof_package_s318.md`
- Visual/metadata artifacts: `10`
- Summary sources: `5`
- Frames: `48`
- Resolution: `960 x 540`
- Preview look: `review`
- Total sphere shapes: `7680`
- Public tuned preview:
  `https://became-dodge-personal-thoroughly.trycloudflare.com`
- Public Blender full48 proof:
  `https://combined-ion-bowl-ted.trycloudflare.com`

## Decision

S318 is the current non-Blender XML preview proof package. It ties the generated
XML scene contract, validation gate, tuned visual preview, public endpoint, and
Blender proof endpoint together for handoff.

## Next

Install Mitsuba or connect another renderer backend, then use S318 as the proof
package for regression comparison.
