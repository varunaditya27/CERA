"""Try permitted reward changes in increasing cost and retain the old rule on failure."""
import copy

from app.rewards.repair_menu import repair_candidates
from app.rewards.repair_verification import verify_repair


def choose_repair(spec, warning_type, candidates, reference, remaining, counterexamples, calibration, earlier,
                  advisor=None, direct_diversity=False, bypass_evidence_gate=False, universal_penalty=False,
                  apply_last_rejected=False):
    if (any(not isinstance(value, bool) for value in (universal_penalty, bypass_evidence_gate, apply_last_rejected))
            or (apply_last_rejected and (bypass_evidence_gate or universal_penalty))):
        raise ValueError('Invalid experimental repair setting')
    attempts = []
    menu = repair_candidates(spec, 'coverage' if universal_penalty else warning_type)
    advice = advisor(warning_type, menu) if advisor is not None and menu else None
    if advice is not None:
        index = advice['option']
        if not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < len(menu):
            raise ValueError('Invalid advised repair index')
        menu = [menu[index]] + menu[:index] + menu[index + 1:]
    for candidate in menu:
        verification = verify_repair(spec, candidate['specification'], warning_type, candidates,
                                     reference, remaining, counterexamples, calibration, earlier,
                                     direct_diversity=direct_diversity, universal_penalty=universal_penalty)
        attempts.append({'term': candidate['term'], 'cost': candidate['cost'],
                         'proposed_weight': candidate['specification']['terms'][candidate['term']]['weight'],
                         'verification': verification})
        if (verification['checks']['allowed_change_and_constraints'] is True if bypass_evidence_gate
                else verification['accepted']):
            return {'status': 'accepted', 'specification': candidate['specification'], 'attempts': attempts,
                    'advice': advice}
    if (apply_last_rejected and attempts and
            attempts[-1]['verification']['checks']['allowed_change_and_constraints'] is True):
        return {'status': 'applied_rejected', 'specification': candidate['specification'], 'attempts': attempts,
                'advice': advice}
    return {'status': 'retained', 'specification': copy.deepcopy(spec), 'attempts': attempts, 'advice': advice}
