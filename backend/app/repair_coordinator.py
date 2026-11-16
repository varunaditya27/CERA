"""Handle triggered warnings in the documented order using saved batch evidence."""
from app.repair_engine import choose_repair
from app.reward_selection import select_batch
from app.warning_checks import diversity_warning

PRIORITY = ('support_shift', 'coverage', 'disagreement', 'diversity')


def handle_warnings(spec, warnings, targets, features, reference, batch_budget, calibration, earlier, failures):
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
        result = choose_repair(spec, kind, features, reference, batch_budget, affected, calibration, earlier)
        spec = result['specification']
        failures = 0 if result['status'] == 'accepted' else failures + 1
        events.append({'warning': kind, 'status': result['status'], 'targets': affected,
                       'attempts': result['attempts'], 'specification': spec, 'consecutive_failures': failures})
        if failures >= spec['abstain_after_failed_repairs']:
            return spec, failures, events, True
    return spec, failures, events, False
