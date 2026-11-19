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

## Replication on new starts

Declared on 19 November 2026, before any of these runs.

The first study reused starts from earlier studies and was designed after seeing them. This replication uses starts that no earlier study used: IRED low-change seeds 71 to 80 and Hydro low-fitness seeds 151 to 160 for each of P06241, P01053 and P0A9X9 (40 new starts), with fixed reward, normal repair and the no-early-stop arm, all other settings as before.

Hypotheses, stated in advance:

1. The no-early-stop arm scores lower than fixed reward in none of the 40 starts (at the 10^-12 tie tolerance).
2. Normal repair scores lower than fixed reward in at least some starts.
3. The no-early-stop arm scores higher than normal repair in most of the starts where normal repair scored lower than fixed reward.

Outcome and counting are as in the protocol above. A hypothesis that fails is reported as failed. This replication is still not a significance test and still uses the same specification, caches and implementation, so it tests repeatability on new starts, not a different method.

### Replication findings

Run on 19 November 2026: 120 runs (three arms on 40 new starts), all completed. The [comparison report](../../../output/multiprotein/repair_continue/replication/comparison.json) and records are in `output/multiprotein/repair_continue/replication/`.

| Protein group | No-stop arm higher than fixed | Tied | Lower | Normal repair lower than fixed | New measurements, normal repair | New measurements, no early stop |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| IRED low-change, seeds 71 to 80 | 0 | 8 | 2 | 3 | 470 | 1,000 |
| Hydro P06241, seeds 151 to 160 | 2 | 8 | 0 | 8 | 290 | 1,000 |
| Hydro P01053, seeds 151 to 160 | 0 | 10 | 0 | 6 | 360 | 1,000 |
| Hydro P0A9X9, seeds 151 to 160 | 0 | 10 | 0 | 8 | 410 | 1,000 |

Against normal repair, the no-early-stop arm was higher in 23 starts, tied in 17 and lower in none.

**Hypotheses.**

1. Failed. The no-early-stop arm scored lower than fixed reward in 2 of 40 starts (IRED seeds 72 and 80, 1.7952 against 1.8335 in both).
2. Held. Normal repair scored lower than fixed reward in 25 of 40 starts.
3. Held. In those 25 starts the no-early-stop arm scored higher than normal repair in 23.

**Reading.** The main pattern replicated on new starts: normal repair loses to fixed reward mostly because it stops early, and the no-early-stop arm recovers nearly all of that loss. The first study's "never lower" did not hold exactly; across all 80 starts the arm was higher than fixed reward in 4, tied in 74 and lower in 2, with small gaps. Two higher results on Hydro P06241 (seeds 153 and 159) show that continuing can find better variants than fixed reward, but they are 2 of 80 and no evidence that the repaired reward is better. The limits above still apply.
