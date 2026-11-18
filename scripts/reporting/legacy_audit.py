#!/usr/bin/env python3
"""Run a flat-layout script from an earlier commit against the current records.

Audits that check recorded source fingerprints need the code they were recorded with. By default this
uses the pre-restructure tag; pass --ref <commit> first for records frozen at an earlier commit.
Example: python3 -m scripts.reporting.legacy_audit audit_mixed_search_comparison \
    output/hybrid/mixed_search_comparison_191_200 configs/reward_spec_example.json /tmp/audit.json
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TAG = 'pre-restructure'
MOVED = {'configs/reward_spec_example.json': 'research/reward_spec_example.json'}


def run(name, args, ref=TAG):
    """Run scripts/<name>.py as it was at <ref>, on the current records. Paths are relative to the repository root."""
    work = Path(tempfile.mkdtemp(prefix='cera-pre-')) / 'tree'
    git = lambda *a, cwd=ROOT: subprocess.run(['git', *a], cwd=cwd, check=True, capture_output=True)
    git('worktree', 'add', '--no-checkout', str(work), ref)
    try:
        git('sparse-checkout', 'set', '--no-cone', 'backend', 'scripts', 'research', 'data', cwd=work)
        git('checkout', cwd=work)
        script = work / 'scripts' / f'{name}.py'
        if not script.exists():
            raise SystemExit(f'{name}.py does not exist in {ref}')
        (work / 'output').mkdir()
        (work / 'output/representations').symlink_to(ROOT / 'output/representations')
        is_path = lambda a: '/' in a or (ROOT / a).exists()
        resolved = [MOVED.get(a) or (str((ROOT / a).resolve()) if is_path(a) else a) for a in args]
        env = dict(os.environ, PYTHONPATH='backend')
        return subprocess.run([sys.executable, str(script), *resolved], cwd=work, env=env).returncode
    finally:
        git('worktree', 'remove', '--force', str(work))


def rerun_with_recorded_code(name, ref=TAG):
    """Called by an audit whose records were produced by earlier code: repeat it with that code."""
    print(f'Recorded code fingerprints differ from the current code; re-running {name} as it was at {ref}.', file=sys.stderr)
    return run(name, sys.argv[1:], ref)


def main():
    argv = sys.argv[1:]
    if not argv:
        raise SystemExit(__doc__)
    ref = TAG
    if argv[0] == '--ref':
        ref, argv = argv[1], argv[2:]
    sys.exit(run(argv[0], argv[1:], ref))


if __name__ == '__main__':
    main()
