"""Try permitted reward changes in increasing cost and retain the old rule on failure."""
import copy

from app.repair_menu import repair_candidates
from app.repair_verification import verify_repair


def choose_repair(spec, warning_type, candidates, reference, remaining, counterexamples, calibration, earlier):
    attempts = []
    for candidate in repair_candidates(spec, warning_type):
        verification = verify_repair(spec, candidate['specification'], warning_type, candidates,
                                     reference, remaining, counterexamples, calibration, earlier)
        attempts.append({'term': candidate['term'], 'cost': candidate['cost'],
                         'proposed_weight': candidate['specification']['terms'][candidate['term']]['weight'],
                         'verification': verification})
        if verification['accepted']:
            return {'status': 'accepted', 'specification': candidate['specification'], 'attempts': attempts}
    return {'status': 'retained', 'specification': copy.deepcopy(spec), 'attempts': attempts}
