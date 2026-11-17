# Multi-protein code review

Reviewed the changes from `e5a3cc4` through `6335ea1` on 17 November 2026, using the two-axis `mattpocock-skills:code-review` workflow and the [comparison draft](multiprotein_comparison_draft.md) as the specification. The two review axes were conducted independently. Findings are based on code inspection; no real protein searches were run for this review.

## Standards

- The evaluator accepts an empty or incomplete recorded source-fingerprint map, weakening the provenance check for altered or damaged records. See `backend/app/analysis/multiprotein_evaluation.py`.
- The evaluator and independent audit decompress run files before checking their compressed fingerprints. A corrupted file can therefore consume substantial resources before rejection. Checking the compressed fingerprint first does not protect against a deliberately replaced file and matching fingerprint, so this is a limited integrity improvement rather than a complete defense.
- Judgment call: the audit function is long and handles several separate checks, making it harder to review. Some independent duplication is intentional because the audit should not reproduce a selector's implementation.
- Judgment call: normal-mode entry points accept four groups with matching but incomplete seed or method lists. The documented runbook supplies the intended scope, but the output label alone does not prove the complete approved study ran.

## Spec

- **Cross-protein settings are not fully matched.** The runbook requires the same code and Python environment, but the evaluator and audit compare only seeds, methods, repair flags and reward-specification hash. A different code version, dependency version or Gemini model could be combined into one report. Dataset, reference and cache fingerprints legitimately differ by protein and should be checked within each group, not equated across groups.
- **The approved study scope is not enforced.** Normal four-protein evaluation accepts any matching nonempty lists of seeds and methods, even though the approved draft specifies seeds 51–60 and nine methods. A reduced study can receive the `four_protein` scope label.
- **Fingerprint and cost reporting are incomplete.** The evaluator checks only source-fingerprint entries that are present, so an empty map passes. It also reports repair counts but omits per-attempt repair costs required in the [roadmap](CERA_research_evidence_and_roadmap.md). These costs are dimensionless rule-change costs, not provider charges.

## Proposed corrections before real runs

1. In both normal-mode entry points, verify the approved seeds, nine-method list and two repair flags, and require identical implementation, Python/dependency versions and Gemini model across groups. Preserve an explicitly labeled partial development mode.
2. Require the complete expected set of recorded predictor source fingerprints and compare each with its manifest. Check compressed fingerprints before decompression, then verify uncompressed fingerprints.
3. Report the recorded cost for every proposed repair and identify which proposed repair was accepted. Keep these values separate from Gemini token usage or financial charges; do not infer unrecorded usage.
4. Test mismatched group manifests, reduced scope, missing source entries, invalid compressed fingerprints and cost reporting on synthetic records, then rerun the full backend suite. Do not start the real study until the corrections pass.

Counts: two documented-standard concerns and two judgment calls; the most consequential standard concern is incomplete source verification. Three spec findings; the most consequential is that different code or models can be silently combined across proteins.
