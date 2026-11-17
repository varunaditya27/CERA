"""Handle triggered warnings in the documented order using saved batch evidence."""
from app.rewards.repair_engine import choose_repair
from app.rewards.reward_selection import select_batch
from app.rewards.warning_checks import diversity_warning

PRIORITY = ('support_shift', 'coverage', 'disagreement', 'diversity')


def handle_warnings(spec, warnings, targets, features, reference, batch_budget, calibration, earlier, failures,
                    advisor=None, direct_diversity=False, stop_on_failed_repairs=True, bypass_evidence_gate=False):
    events = []
    for kind in PRIORITY:
        warning = warnings[kind]
        if warning['status'] != 'triggered':
            continue
        replayed = [entry['id'] for entry in select_batch(spec, features, reference, batch_budget)]
        if kind == 'diversity':
            recheck = diversity_warning({i: features[i]['sequence'] for i in replayed})
            if recheck['status'] != 'triggered':
                events.append({'warning': kind, 'status': 'recheck_not_triggered', 'replayed_ids': replayed})
                continue
        affected = [identifier for identifier in targets[kind] if identifier in replayed]
        if not affected:
            events.append({'warning': kind, 'status': 'no_replayed_targets', 'replayed_ids': replayed})
            continue
        result = choose_repair(spec, kind, features, reference, batch_budget, affected, calibration, earlier,
                               advisor=advisor, direct_diversity=direct_diversity,
                               bypass_evidence_gate=bypass_evidence_gate)
        spec = result['specification']
        failures = 0 if result['status'] == 'accepted' else failures + 1
        events.append({'warning': kind, 'status': result['status'], 'targets': affected,
                       'attempts': result['attempts'], 'advice': result.get('advice'),
                       'specification': spec, 'consecutive_failures': failures})
        if stop_on_failed_repairs and failures >= spec['abstain_after_failed_repairs']:
            return spec, failures, events, True
    return spec, failures, events, False
