import json


def write_new_or_confirm_saved(path, result, ignore=('audit_script_sha256',)):
    """Write a new audit record, or confirm that the result matches the record already saved there."""
    if not path.exists():
        with path.open('x', encoding='utf-8') as file:
            json.dump(result, file, indent=2)
            file.write('\n')
        return 'written'
    saved = json.loads(path.read_text(encoding='utf-8'))
    keep = lambda record: {key: value for key, value in record.items() if key not in ignore}
    if keep(saved) != keep(result):
        raise ValueError('The audit result differs from the saved audit record')
    return 'matches the saved audit record'
