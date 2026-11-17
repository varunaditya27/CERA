"""Choose range-setting examples from already revealed measurements."""


def recent_calibration(history, known_ids):
    entries = list(history)
    known = set(known_ids)
    if (len(entries) < 20 or any(not isinstance(i, str) or not i or not isinstance(covered, bool)
                                 for i, covered in entries)
            or len({i for i, _ in entries}) != len(entries)
            or not {i for i, _ in entries}.issubset(known)):
        raise ValueError('Invalid revealed calibration history')
    return sorted(i for i, _ in entries[-20:])
