# Controlled unfamiliar-candidate warning findings

The [protocol](support_warning_simulation_protocol.md) constructed one-dimensional near and far candidate batches with known independent score-miss probabilities. A shifted batch was defined by its constructed distances, independently of the warning result. This is a synthetic probe of the implemented compound rule, not a protein-data estimate or a claim that distance caused prediction misses.

| Constructed condition | Candidate distances | Per-score miss probability | Warnings | Exact warning probability under this independent model |
| --- | --- | ---: | ---: | ---: |
| Reference | All near | 10% | 0/1,000 | 0% by construction |
| Shifted, well covered | All far | 10% | 74/1,000 | 7.02% |
| Shifted, poorly covered | All far | 50% | 943/1,000 | 94.53% |

The warning requires at least three candidates to be both far and outside their ranges. In this constructed experiment, all far batches are labeled as shifted even if their scores remain inside the ranges. Therefore 926 well-covered shifted batches did not trigger; this is expected from the compound definition and should not be described as a general biological false-negative rate. The near reference cannot trigger by construction, so its zero false alarms do not estimate false alarms among other negative cases.

Using a separate artificial 50/50 mixture of 1,000 shifted and 1,000 reference batches for each comparison, observed recall was 7.4% for well-covered shifts and 94.3% for poorly covered shifts. Precision was 100% in both mixtures because the constructed reference condition cannot trigger; F1 was about 0.138 and 0.971, respectively. These values depend on the constructed cases and mixture, and do not measure real-world prevalence or accuracy.

The [simulation output](../output/support_warning_simulation.json) records the seed, distances, counts, exact binomial probabilities, versions and source fingerprints. A separate [reproducible audit](../output/support_warning_simulation_audit.json) regenerated all 3,000 batches without calling the warning, recomputed distances and trigger conditions, checked exact probabilities using SciPy, and rejected altered distances in testing. The simulation output SHA-256 was `7f745bfaea4372a7584877f08f74aa5a66f1ef0c0def429af91413fccb23e944`; the audit script SHA-256 was `df3ca8617b635a0a6ff174802a491344c76ea8178abab1802ce7d0bc1c93177d`. All 131 backend tests passed before this run. No protein scores, model thresholds or provider settings were changed.
