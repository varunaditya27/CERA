import copy
import gzip
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from contextlib import redirect_stdout

from app.analysis.multiprotein_evaluation import repair_costs, verified_record
from app.analysis.study_protocol import DATASETS, SPECIFICATION_SHA256, validate_manifests
from app.experiments.repeated_runs import METHODS
from app.llm.goal_compiler import DEFAULT_SPEC

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from audit_matched_proteins import check_repair_cost, check_repair_order, main as audit_main
from evaluate_matched_proteins import main as evaluate_main


def manifests():
    common = {'initial_pool': 'eligible', 'seeds': list(range(51, 61)), 'methods': list(METHODS), 'targeted_disagreement': True,
              'direct_diversity': True, 'specification_sha256': SPECIFICATION_SHA256, 'code_sha256': {'module': 'hash'},
              'python': '3.11', 'versions': {'numpy': '1'}, 'gemini_model': 'model'}
    return [dict(copy.deepcopy(common), dataset=name, data_sha256=name, reference_sha256=name,
                 representation_cache_sha256=name) for name in sorted(DATASETS)]


class StudyProtocolTests(unittest.TestCase):
    def test_full_scope_and_group_consistency(self):
        original = manifests()
        validate_manifests(original)
        for key, value in (('code_sha256', {'module': 'changed'}), ('python', '3.12'),
                           ('versions', {'numpy': '2'}), ('gemini_model', 'other')):
            altered = copy.deepcopy(original)
            altered[-1][key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'settings differ'):
                validate_manifests(altered)
        for key, value in (('seeds', [51]), ('methods', ['random']),
                           ('targeted_disagreement', False), ('direct_diversity', False), ('specification_sha256', 'wrong')):
            altered = copy.deepcopy(original)
            for manifest in altered:
                manifest[key] = value
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'approved protocol'):
                validate_manifests(altered)
        with self.assertRaisesRegex(ValueError, 'all four'):
            validate_manifests(original[:1])
        validate_manifests(original[:1], partial_development=True)

    def test_four_group_workflow_preserves_failures_and_rejects_mismatch_before_data_access(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            spec = root / 'spec.json'
            spec.write_bytes((Path(__file__).resolve().parents[2] / 'research/reward_spec_example.json').read_bytes())
            reference = root / 'reference.fasta'
            reference.write_text('>synthetic\nAAA\n')
            groups = manifests()
            roots = []
            for manifest in groups:
                manifest.update(specification_sha256=hashlib.sha256(spec.read_bytes()).hexdigest(),
                                data_sha256='data', reference_sha256='reference')
                group = root / manifest['dataset']
                group.mkdir()
                roots.append(group)
                (group / 'manifest.json').write_text(json.dumps(manifest))
                for seed in manifest['seeds']:
                    for method in manifest['methods']:
                        path = group / f'seed_{seed:02d}' / method
                        path.mkdir(parents=True)
                        (path / 'status.json').write_text(json.dumps({'status': 'failed', 'error_type': 'SyntheticFailure'}))
            scores = {f'i{i:03}': float(i) for i in range(120)}
            sequences = {identifier: 'AAA' for identifier in scores}
            loader = lambda *_: (sequences, scores, [], 'data', 'reference')
            source = lambda _: (root / 'unused', reference, loader)
            report = root / 'report.json'
            argv = ['evaluate_matched_proteins.py', str(report), *map(str, roots), '--specification', str(spec)]
            with patch('evaluate_matched_proteins.dataset_source', side_effect=source), patch.object(sys, 'argv', argv):
                evaluate_main()
            result = json.loads(report.read_text())
            self.assertEqual(result['scope'], 'four_protein')
            self.assertEqual([len(group['summaries']) for group in result['groups']], [90] * 4)
            self.assertTrue(all(row['best_observed_difference'] is None for group in result['groups']
                                for row in group['paired_to_fixed']))
            with patch('audit_matched_proteins.dataset_source', side_effect=source), \
                 patch('audit_matched_proteins.representations', return_value={}), \
                 patch.object(sys, 'argv', ['audit_matched_proteins.py', *map(str, roots)]), \
                 redirect_stdout(io.StringIO()) as output:
                audit_main()
            self.assertEqual([group['failed'] for group in json.loads(output.getvalue())['groups']], [90] * 4)
            changed = json.loads((roots[-1] / 'manifest.json').read_text())
            changed['code_sha256'] = {'module': 'different'}
            (roots[-1] / 'manifest.json').write_text(json.dumps(changed))
            with patch('evaluate_matched_proteins.dataset_source') as source_mock, patch.object(sys, 'argv', argv), \
                 self.assertRaisesRegex(ValueError, 'settings differ'):
                evaluate_main()
            source_mock.assert_not_called()
            with patch('audit_matched_proteins.dataset_source') as source_mock, \
                 patch.object(sys, 'argv', ['audit_matched_proteins.py', *map(str, roots)]), \
                 self.assertRaisesRegex(ValueError, 'settings differ'):
                audit_main()
            source_mock.assert_not_called()

    def test_compressed_digest_is_checked_before_decompression(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'record.gz'
            raw = b'valid record'
            blob = gzip.compress(raw, mtime=0)
            path.write_bytes(blob)
            status = {'gzip_sha256': hashlib.sha256(blob).hexdigest(),
                      'uncompressed_sha256': hashlib.sha256(raw).hexdigest()}
            self.assertEqual(verified_record(path, status), raw)
            with patch('app.analysis.multiprotein_evaluation.gzip.decompress') as decompress:
                with self.assertRaisesRegex(ValueError, 'Compressed run fingerprint'):
                    verified_record(path, dict(status, gzip_sha256='wrong'))
                decompress.assert_not_called()
            with self.assertRaisesRegex(ValueError, 'Uncompressed run fingerprint'):
                verified_record(path, dict(status, uncompressed_sha256='wrong'))

    def test_repair_attempt_order_matches_rule_and_advice(self):
        row = DEFAULT_SPEC['terms']['diversity_bonus']
        values = [min(row['allowed_range'][1], row['weight'] + step) for step in (0.25, 0.5, 1.0)]
        options = [{'option': i, 'term': 'diversity_bonus', 'weight': value,
                    'cost': (value - row['weight']) / (row['allowed_range'][1] - row['allowed_range'][0]) + 0.05}
                   for i, value in enumerate(values)]
        attempts = [{'term': option['term'], 'proposed_weight': option['weight']} for option in options]
        action = {'warning': 'diversity', 'status': 'retained', 'attempts': attempts, 'advice': None}
        check_repair_order(DEFAULT_SPEC, 'repair', action)
        bad = dict(action, attempts=list(reversed(attempts)))
        with self.assertRaisesRegex(ValueError, 'order mismatch'):
            check_repair_order(DEFAULT_SPEC, 'repair', bad)
        advised = dict(action, attempts=[attempts[2], attempts[0], attempts[1]],
                       advice={'source': 'gemini', 'option': 2, 'options': options})
        check_repair_order(DEFAULT_SPEC, 'gemini_repair', advised)
        bad_fallback = dict(advised, advice={'source': 'fallback', 'option': 2, 'options': options})
        with self.assertRaisesRegex(ValueError, 'Invalid recorded repair advice'):
            check_repair_order(DEFAULT_SPEC, 'gemini_repair', bad_fallback)
        bad = dict(advised, attempts=[attempts[2], attempts[2], attempts[1]])
        with self.assertRaisesRegex(ValueError, 'order mismatch'):
            check_repair_order(DEFAULT_SPEC, 'gemini_repair', bad)
        with self.assertRaisesRegex(ValueError, 'Incomplete repair menu'):
            check_repair_order(DEFAULT_SPEC, 'repair', dict(action, attempts=attempts[:1]))

    def test_costs_preserve_attempts_and_acceptance(self):
        attempts = [{'term': 'diversity_bonus', 'proposed_weight': 0.35, 'cost': 0.3,
                     'verification': {'accepted': False}},
                    {'term': 'diversity_bonus', 'proposed_weight': 0.6, 'cost': 0.55,
                     'verification': {'accepted': True}}]
        action = {'warning': 'diversity', 'status': 'accepted', 'attempts': attempts}
        self.assertEqual([row['cost'] for row in repair_costs([action])], [0.3, 0.55])
        for attempt in attempts:
            check_repair_cost(DEFAULT_SPEC, 'diversity', attempt)
        changed = dict(attempts[0], cost=0.2)
        with self.assertRaisesRegex(ValueError, 'Repair cost mismatch'):
            check_repair_cost(DEFAULT_SPEC, 'diversity', changed)
        changed = dict(attempts[0], proposed_weight=0.36)
        with self.assertRaisesRegex(ValueError, 'outside allowed menu'):
            check_repair_cost(DEFAULT_SPEC, 'diversity', changed)
        self.assertEqual([row['accepted'] for row in repair_costs([action])], [False, True])
        bad = copy.deepcopy(action)
        bad['attempts'][0]['cost'] = float('nan')
        with self.assertRaises(ValueError):
            repair_costs([bad])
        bad = copy.deepcopy(action)
        bad['status'] = 'retained'
        with self.assertRaises(ValueError):
            repair_costs([bad])


if __name__ == '__main__':
    unittest.main()
