"""Try permitted reward changes in increasing cost and retain the old rule on failure."""
import copy

from app.repair_menu import repair_candidates
from app.repair_verification import verify_repair


def choose_repair(spec, warning_type, candidates, reference, remaining, counterexamples, calibration, earlier,
                  advisor=None):
    attempts = []
    menu = repair_candidates(spec, warning_type)
    advice = advisor(warning_type, menu) if advisor is not None and menu else None
    if advice is not None:
        index = advice['option']
        if not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < len(menu):
            raise ValueError('Invalid advised repair index')
        menu = [menu[index]] + menu[:index] + menu[index + 1:]
    for candidate in menu:
        verification = verify_repair(spec, candidate['specification'], warning_type, candidates,
                                     reference, remaining, counterexamples, calibration, earlier)
        attempts.append({'term': candidate['term'], 'cost': candidate['cost'],
                         'proposed_weight': candidate['specification']['terms'][candidate['term']]['weight'],
                         'verification': verification})
        if verification['accepted']:
            return {'status': 'accepted', 'specification': candidate['specification'], 'attempts': attempts,
                    'advice': advice}
    return {'status': 'retained', 'specification': copy.deepcopy(spec), 'attempts': attempts, 'advice': advice}
