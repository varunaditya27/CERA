<div align="center">

# Repair without early stopping

Protocol and findings

</div>

## Protocol

Written on 19 November 2026, before the comparison was run.

**Question.** In the four-protein, IRED low-change and Hydro low-fitness studies, repair never beat fixed reward at its stopping point, and repair often stopped early after failed checks. Is the lack of improvement caused by the repairs, or by stopping early and so using fewer measurements? Earlier work answered this only on Amylase development data ([ablations](ablations.md)).

**Arm.** `repair_continue` is the rule-based repair policy with the targeted-disagreement and direct-diversity checks, identical to `repair` in every respect except that it never stops after failed repairs. It spends the same 100-measurement budget as fixed reward. The pilot code allowed this only on Amylase, as a guard against using evaluation data to design the method; this study removes the guard for repair runs on purpose and is therefore labelled post hoc.

**Data.** The same starts, specification and representation caches as the original studies: IRED low-change seeds 61 to 70, and Hydro low-fitness seeds 141 to 150 for each of P06241, P01053 and P0A9X9 (40 starts). The IRED and Hydro starting pools carry the limitations described in their own documents. Normal `repair` is run again as well; its records must equal the original ones, which checks that removing the guard changed no behaviour.

**Outcome.** The best measured score after the run, compared start by start with the original fixed-reward and repair runs. Differences of at most 10^-12 count as ties. The counts of higher, tied and lower are reported per protein group, without a significance test.

**Status.** Exploratory and post hoc. The starts were already used by earlier studies, so they are not independent replications, and the design was chosen after seeing those results.

## Findings

Run on 19 November 2026: 80 runs (10 starts each for IRED and three Hydro proteins, normal repair repeated plus the new arm), all completed. The [comparison report](../../../output/multiprotein/repair_continue/comparison.json) and the run records are in `output/multiprotein/repair_continue/`.

**Behaviour check.** The repeated normal-repair runs matched the original records in all 40 starts (curve and stop reason), so removing the guard changed nothing for runs that still stop early.

**Repair without stopping, against fixed reward** (best score after the run):

| Protein group | Repair higher | Tied | Repair lower | New measurements, normal repair | New measurements, no early stop |
| --- | ---: | ---: | ---: | ---: | ---: |
| IRED low-change | 2 | 8 | 0 | 410 | 1,000 |
| Hydro P06241 | 0 | 10 | 0 | 290 | 1,000 |
| Hydro P01053 | 0 | 10 | 0 | 330 | 1,000 |
| Hydro P0A9X9 | 0 | 10 | 0 | 510 | 1,000 |

Without early stopping, repair never scored below fixed reward in 40 starts: 38 ties and 2 higher (IRED seeds 61 and 66, 2.4175 against 1.7952 and 1.8043 against 1.6110). Every run used the whole 100-measurement budget. Against normal repair, which stopped early, the new arm scored higher in 28 starts (IRED 3, P06241 10, P01053 9, P0A9X9 6), tied in 12 and lower in none.

**Reading.** In the earlier studies repair scored lower than fixed reward in 5 of 40 starts at its stopping point (IRED) and in 25 of 30 (Hydro). Those deficits disappear when repair is allowed to keep measuring, which indicates that early stopping, not the repaired reward, explains them. It does not show that repair helps: the new arm matches fixed reward in 38 of 40 starts, and the two IRED gains could come from a different selection path rather than a better reward.

**Limits.** Exploratory and post hoc; the starts were reused from earlier studies, so these are not independent replications, and IRED and Hydro starts have the limitations described in their own documents. The new records were checked for fingerprints and for matching the original starting observations, but the selections and repair replays of the new arm were not independently reconstructed by an audit script. Ties are not evidence of equivalence. No significance test was run.

**Commands.**

```sh
PYTHONPATH=backend:. python3 -m scripts.multiprotein.run_matched_proteins output/multiprotein/repair_continue/ired_low_change_61_70 --dataset ired --initial-pool train --seeds 61 62 63 64 65 66 67 68 69 70 --methods repair repair_continue --specification configs/reward_spec_example.json --targeted-disagreement --direct-diversity
PYTHONPATH=backend:. python3 -m scripts.multiprotein.compare_repair_continue output/multiprotein/repair_continue/comparison.json --pair <original root> <new root> [--pair ...]
```

The Hydro runs add `--dataset hydro-<protein> --hydro-low-fitness` and seeds 141 to 150, as in [Hydro low-fitness start](../multiprotein/hydro_low_fitness.md).
