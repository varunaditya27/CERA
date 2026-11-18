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


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    argv = sys.argv[1:]
    ref = TAG
    if argv[0] == '--ref':
        ref, argv = argv[1], argv[2:]
    name, args = argv[0], argv[1:]
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
        resolved = [MOVED.get(a, str((ROOT / a).resolve()) if (ROOT / a).exists() or (ROOT / a).parent.exists() and not a.startswith('-') else a) for a in args]
        env = dict(os.environ, PYTHONPATH='backend')
        sys.exit(subprocess.run([sys.executable, str(script), *resolved], cwd=work, env=env).returncode)
    finally:
        git('worktree', 'remove', '--force', str(work))


if __name__ == '__main__':
    main()
