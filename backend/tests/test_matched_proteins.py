import copy
import csv
import hashlib
import io
import os
import gzip
import itertools
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from contextlib import redirect_stdout

import numpy as np

from app.features.representations import sequence_id
from app.llm.goal_compiler import DEFAULT_SPEC
from app.analysis.multiprotein_evaluation import evaluate_group, terminal_statuses
from app.datasets.flip2 import load_flip2

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from run_matched_proteins import main
from evaluate_matched_proteins import main as evaluate_main
from audit_matched_proteins import audit_group, main as audit_main


class MatchedProteinTests(unittest.TestCase):
    def test_low_change_start_and_independent_audit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, reference, spec, output = (root / name for name in ('data.csv', 'reference.fasta', 'spec.json', 'runs'))
            reference.write_text('>synthetic\nAAA\n')
            sequences = ['A' + a + b for a, b in itertools.islice(itertools.product('ACDEFGHIKLMNPQRSTVWY', repeat=2), 120)]
            with data.open('w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['sequence', 'target', 'set', 'validation'])
                writer.writerows((sequence, index / 100, 'train' if index < 110 else 'test',
                                  'True' if index % 3 == 0 else 'False')
                                 for index, sequence in enumerate(sequences))
            spec.write_text(json.dumps(DEFAULT_SPEC))
            vectors = {sequence_id(sequence): np.asarray([i / 120, (i % 19) / 19], dtype=np.float32)
                       for i, sequence in enumerate(sequences)}
            methods = ['random', 'greedy', 'fixed', 'repair', 'gemini_repair', 'ucb', 'ei', 'genetic', 'adalead']
            argv = ['run_matched_proteins.py', str(output), '--dataset', 'ired', '--seeds', '7',
                    '--methods', *methods, '--specification', str(spec), '--initial-pool', 'train',
                    '--targeted-disagreement', '--direct-diversity']
            with patch('app.datasets.ired.DATA', data), patch('app.datasets.ired.REFERENCE', reference), \
                 patch('app.features.ired_representations.load_verified_representations', return_value=vectors), \
                 patch.dict(os.environ, {'GEMINI_API_KEY': 'synthetic-key', 'GEMINI_MODEL': 'synthetic-model'}), \
                 patch('run_matched_proteins.request_repair', return_value=('{}', {})), \
                 patch.object(sys, 'argv', argv), redirect_stdout(io.StringIO()):
                main()
            manifest = json.loads((output / 'manifest.json').read_text())
            self.assertEqual(manifest['initial_pool'], 'train')
            seqs, scores, train, data_hash, ref_hash = load_flip2(data, reference, 4)
            random_events = [json.loads(line) for line in gzip.decompress(
                (output / 'seed_07/random/run.jsonl.gz').read_bytes()).splitlines()]
            flagged = {sequence_id(sequence) for index, sequence in enumerate(sequences[:110]) if index % 3 == 0}
            self.assertTrue(set(random_events[0]['initial']) & flagged)
            statuses = terminal_statuses(output, manifest)
            result = evaluate_group(output, manifest, statuses, scores, data_hash, ref_hash, DEFAULT_SPEC,
                                    train, seqs, 'AAA')
            self.assertEqual(len(result['summaries']), 9)
            self.assertTrue(all(row['status'] == 'completed' for row in result['summaries']))
            self.assertEqual(sum(result['summaries'][0]['selected_mutation_counts'].values()), 20)
            self.assertEqual(audit_group(output, manifest, statuses, seqs, scores, 'AAA', vectors, train)['completed'], 9)
            changed = list(reversed(train))
            with self.assertRaisesRegex(ValueError, 'Starting observations'):
                evaluate_group(output, manifest, statuses, scores, data_hash, ref_hash, DEFAULT_SPEC,
                               changed, seqs, 'AAA')
            with self.assertRaisesRegex(ValueError, 'Initial observations'):
                audit_group(output, manifest, statuses, seqs, scores, 'AAA', vectors, changed)
            record = output / 'seed_07/greedy/run.jsonl.gz'
            original = [json.loads(line) for line in gzip.decompress(record.read_bytes()).splitlines()]
            status_path = record.parent / 'status.json'
            for name, value in (('stop_on_failed_repairs', False), ('bypass_evidence_gate', True),
                                ('disabled_repair_terms', ['distance_penalty']), ('universal_penalty', True),
                                ('apply_last_rejected', True), ('rollback_monitor', True), ('reactive_calibration', True)):
                with self.subTest(name=name):
                    events = copy.deepcopy(original)
                    events[1]['settings'][name] = value
                    raw = b''.join((json.dumps(event) + '\n').encode() for event in events)
                    blob = gzip.compress(raw, mtime=0)
                    record.write_bytes(blob)
                    altered = json.loads(status_path.read_text())
                    altered.update(gzip_sha256=hashlib.sha256(blob).hexdigest(), uncompressed_sha256=hashlib.sha256(raw).hexdigest())
                    status_path.write_text(json.dumps(altered))
                    statuses = terminal_statuses(output, manifest)
                    with self.assertRaisesRegex(ValueError, 'Method configuration'):
                        evaluate_group(output, manifest, statuses, scores, data_hash, ref_hash, DEFAULT_SPEC,
                                       train, seqs, 'AAA')
                    with self.assertRaisesRegex(ValueError, 'Predictor configuration'):
                        audit_group(output, manifest, statuses, seqs, scores, 'AAA', vectors, train)

    def test_hydro_train_start_keeps_all_candidates_and_audits(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, reference, spec, output = (root / name for name in ('data.csv', 'reference.fasta', 'spec.json', 'runs'))
            reference.write_text('>synthetic\n' + 'A' * 57 + '\n')
            sequences = ['A' * 55 + a + b for a, b in itertools.islice(
                itertools.product('ACDEFGHIKLMNPQRSTVWY', repeat=2), 120)]
            with data.open('w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['sequence', 'target', 'set', 'validation'])
                writer.writerows((sequence, index / 100, 'train' if index < 110 else 'test', 'False')
                                 for index, sequence in enumerate(sequences))
            spec.write_text(json.dumps(DEFAULT_SPEC))
            vectors = {sequence_id(sequence): np.asarray([i / 120, (i % 19) / 19], dtype=np.float32)
                       for i, sequence in enumerate(sequences)}
            argv = ['run_matched_proteins.py', str(output), '--dataset', 'hydro-P06241', '--seeds', '7',
                    '--methods', 'random', 'greedy', '--specification', str(spec), '--initial-pool', 'train']
            with patch('app.datasets.hydro.DATA', data), patch.dict('app.datasets.hydro.REFERENCES', {'P06241': reference}), \
                 patch('app.features.hydro_representations.load_verified_representations', return_value=vectors), \
                 patch.object(sys, 'argv', argv), redirect_stdout(io.StringIO()):
                with self.assertRaisesRegex(ValueError, 'explicit low-fitness flag'):
                    main()
                with patch.object(sys, 'argv', argv + ['--hydro-low-fitness']):
                    main()
            manifest = json.loads((output / 'manifest.json').read_text())
            seqs, scores, train, data_hash, ref_hash = load_flip2(data, reference, 4, {57})
            statuses = terminal_statuses(output, manifest)
            result = evaluate_group(output, manifest, statuses, scores, data_hash, ref_hash, DEFAULT_SPEC,
                                    train, seqs, 'A' * 57)
            self.assertEqual([row['selected_split_counts'] for row in result['summaries']],
                             [{'train': 10, 'test': 10}] * 2)
            self.assertEqual(audit_group(output, manifest, statuses, seqs, scores, 'A' * 57, vectors, train)['completed'], 2)
            for method in ('random', 'greedy'):
                raw = gzip.decompress((output / f'seed_07/{method}/run.jsonl.gz').read_bytes())
                events = [json.loads(line) for line in raw.splitlines()]
                self.assertTrue(set(events[0]['initial']).issubset(train))
                self.assertEqual(len({i for e in events if e['event'] == 'selection' for i in e['ids']}), 20)

    def test_synthetic_comparison_and_resume(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, reference, spec, output = (root / name for name in ('data.csv', 'reference.fasta', 'spec.json', 'runs'))
            reference.write_text('>synthetic\nAAA\n')
            sequences = ['A' + a + b for a, b in itertools.islice(itertools.product('ACDEFGHIKLMNPQRSTVWY', repeat=2), 120)]
            with data.open('w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['sequence', 'target', 'set', 'validation'])
                writer.writerows((sequence, index / 100, 'train' if index < 110 else 'test', 'False')
                                 for index, sequence in enumerate(sequences))
            spec.write_text(json.dumps(DEFAULT_SPEC))
            vectors = {sequence_id(sequence): np.asarray([i / 120, (i % 19) / 19], dtype=np.float32)
                       for i, sequence in enumerate(sequences)}
            argv = ['run_matched_proteins.py', str(output), '--dataset', 'ired', '--seeds', '7',
                    '--methods', 'random', 'greedy', '--specification', str(spec)]
            with patch('app.datasets.ired.DATA', data), patch('app.datasets.ired.REFERENCE', reference), \
                 patch('app.features.ired_representations.load_verified_representations', return_value=vectors), \
                 patch.object(sys, 'argv', argv):
                main()
                manifest = json.loads((output / 'manifest.json').read_text())
                self.assertEqual(manifest['initial_pool'], 'eligible')
                records = []
                for method in ('random', 'greedy'):
                    path = output / 'seed_07' / method
                    self.assertEqual(json.loads((path / 'status.json').read_text())['status'], 'completed')
                    records.append([json.loads(line) for line in gzip.decompress((path / 'run.jsonl.gz').read_bytes()).splitlines()])
                self.assertEqual(records[0][0]['initial'], records[1][0]['initial'])
                self.assertEqual(records[0][0]['initial_pool'], 'eligible')
                partial_argv = ['evaluate_matched_proteins.py', str(root / 'partial.json'), str(output),
                                '--specification', str(spec)]
                with patch.object(sys, 'argv', partial_argv), patch('evaluate_matched_proteins.dataset_source') as source, \
                     self.assertRaisesRegex(ValueError, 'all four protein groups'):
                    evaluate_main()
                source.assert_not_called()
                incomplete = root / 'incomplete'
                incomplete.mkdir()
                incomplete_manifest = dict(manifest, dataset='hydro-P06241')
                (incomplete / 'manifest.json').write_text(json.dumps(incomplete_manifest))
                incomplete_argv = ['evaluate_matched_proteins.py', str(root / 'incomplete.json'), str(output),
                                   str(incomplete), '--specification', str(spec), '--allow-partial-development']
                with patch.object(sys, 'argv', incomplete_argv), patch('evaluate_matched_proteins.dataset_source') as source, \
                     self.assertRaisesRegex(ValueError, 'terminal statuses'):
                    evaluate_main()
                source.assert_not_called()
                report = root / 'report.json'
                eval_argv = ['evaluate_matched_proteins.py', str(report), str(output), '--specification', str(spec), '--allow-partial-development']
                missing = output / 'seed_07' / 'greedy' / 'status.json'
                contents = missing.read_text()
                missing.unlink()
                with patch.object(sys, 'argv', eval_argv), patch('evaluate_matched_proteins.dataset_source') as source, \
                     self.assertRaisesRegex(ValueError, 'terminal statuses'):
                    evaluate_main()
                source.assert_not_called()
                missing.write_text(contents)
                with patch.object(sys, 'argv', eval_argv):
                    evaluate_main()
                summaries = json.loads(report.read_text())['groups'][0]['summaries']
                self.assertEqual([row['method'] for row in summaries], ['random', 'greedy'])
                self.assertEqual([row['new_measurements'] for row in summaries], [20, 20])
                self.assertIsNone(summaries[0]['recovery'])
                self.assertEqual(summaries[1]['recovery']['status'], 'no_warning')
                with patch.object(sys, 'argv', eval_argv), self.assertRaises(FileExistsError):
                    evaluate_main()
                with patch.object(sys, 'argv', argv + ['--resume']):
                    main()
                changed = copy.deepcopy(DEFAULT_SPEC)
                changed['terms']['uncertainty_penalty']['weight'] = 0.75
                spec.write_text(json.dumps(changed))
                with patch.object(sys, 'argv', argv + ['--resume']), self.assertRaisesRegex(ValueError, 'changed inputs'):
                    main()
                spec.write_text(json.dumps(DEFAULT_SPEC))
                path = output / 'seed_07' / 'random' / 'run.jsonl.gz'
                path.write_bytes(path.read_bytes() + b'altered')
                with patch.object(sys, 'argv', argv + ['--resume']), self.assertRaisesRegex(ValueError, 'fingerprint mismatch'):
                    main()
                all_output = root / 'all_methods'
                methods = ['random', 'greedy', 'fixed', 'repair', 'gemini_repair', 'ucb', 'ei', 'genetic', 'adalead']
                all_argv = ['run_matched_proteins.py', str(all_output), '--dataset', 'ired', '--seeds', '7',
                            '--methods', *methods, '--specification', str(spec), '--targeted-disagreement', '--direct-diversity']
                with patch.dict(os.environ, {'GEMINI_API_KEY': 'synthetic-key', 'GEMINI_MODEL': 'synthetic-model'}), \
                     patch('run_matched_proteins.request_repair', return_value=('{}', {})), \
                     patch.object(sys, 'argv', all_argv):
                    main()
                all_report = root / 'all_report.json'
                with patch.object(sys, 'argv', ['evaluate_matched_proteins.py', str(all_report), str(all_output),
                                               '--specification', str(spec), '--allow-partial-development']):
                    evaluate_main()
                all_group = json.loads(all_report.read_text())['groups'][0]
                all_rows = all_group['summaries']
                self.assertEqual(len(all_group['paired_to_fixed']), 8)
                self.assertTrue(all(row['baseline'] == 'fixed' for row in all_group['paired_to_fixed']))
                self.assertEqual([row['method'] for row in all_rows], methods)
                self.assertTrue(all(row['status'] == 'completed' for row in all_rows))
                fixed_status_path = all_output / 'seed_07/fixed/status.json'
                fixed_status = fixed_status_path.read_text()
                fixed_status_path.write_text(json.dumps({'status': 'failed', 'error_type': 'SyntheticFailure'}))
                missing_report = root / 'missing_fixed.json'
                with patch.object(sys, 'argv', ['evaluate_matched_proteins.py', str(missing_report), str(all_output),
                                               '--specification', str(spec), '--allow-partial-development']):
                    evaluate_main()
                missing_pairs = json.loads(missing_report.read_text())['groups'][0]['paired_to_fixed']
                self.assertTrue(all(row['baseline_status'] == 'failed' and row['best_observed_difference'] is None
                                    for row in missing_pairs))
                fixed_status_path.write_text(fixed_status)
                with patch.object(sys, 'argv', ['audit_matched_proteins.py', str(all_output), '--allow-partial-development']), \
                     redirect_stdout(io.StringIO()) as audit_output:
                    audit_main()
                self.assertEqual(json.loads(audit_output.getvalue())['groups'][0]['completed'], 9)
                greedy_path = all_output / 'seed_07/greedy/run.jsonl.gz'
                original_blob = greedy_path.read_bytes()
                original_status = (greedy_path.parent / 'status.json').read_text()
                altered_start = [json.loads(line) for line in gzip.decompress(original_blob).splitlines()]
                first_id = next(iter(altered_start[0]['initial']))
                altered_start[0]['initial'][first_id] += 1
                raw_start = b''.join((json.dumps(event) + '\n').encode() for event in altered_start)
                blob_start = gzip.compress(raw_start, mtime=0)
                greedy_path.write_bytes(blob_start)
                changed_status = json.loads(original_status)
                changed_status.update(gzip_sha256=hashlib.sha256(blob_start).hexdigest(),
                                      uncompressed_sha256=hashlib.sha256(raw_start).hexdigest())
                (greedy_path.parent / 'status.json').write_text(json.dumps(changed_status))
                with patch.object(sys, 'argv', ['evaluate_matched_proteins.py', str(root / 'bad_start.json'),
                                               str(all_output), '--specification', str(spec), '--allow-partial-development']), \
                     self.assertRaisesRegex(ValueError, 'Starting observations'):
                    evaluate_main()
                greedy_path.write_bytes(original_blob)
                (greedy_path.parent / 'status.json').write_text(original_status)
                altered_sources = [json.loads(line) for line in gzip.decompress(original_blob).splitlines()]
                setup = next(event['settings'] for event in altered_sources if event['event'] == 'method')
                setup['source_sha256'] = {}
                raw_sources = b''.join((json.dumps(event) + '\n').encode() for event in altered_sources)
                blob_sources = gzip.compress(raw_sources, mtime=0)
                greedy_path.write_bytes(blob_sources)
                changed_status = json.loads(original_status)
                changed_status.update(gzip_sha256=hashlib.sha256(blob_sources).hexdigest(),
                                      uncompressed_sha256=hashlib.sha256(raw_sources).hexdigest())
                (greedy_path.parent / 'status.json').write_text(json.dumps(changed_status))
                with patch.object(sys, 'argv', ['evaluate_matched_proteins.py', str(root / 'bad_source.json'),
                                               str(all_output), '--specification', str(spec), '--allow-partial-development']), \
                     self.assertRaisesRegex(ValueError, 'source fingerprints'):
                    evaluate_main()
                with patch.object(sys, 'argv', ['audit_matched_proteins.py', str(all_output), '--allow-partial-development']), \
                     self.assertRaisesRegex(ValueError, 'source fingerprints'):
                    audit_main()
                greedy_path.write_bytes(original_blob)
                (greedy_path.parent / 'status.json').write_text(original_status)
                altered_path = all_output / 'seed_07/greedy/run.jsonl.gz'
                altered = [json.loads(line) for line in gzip.decompress(altered_path.read_bytes()).splitlines()]
                selection = next(e for e in altered if e['event'] == 'selection')
                selection['ids'][0] = next(i for i in selection['prediction_ranges'] if i not in selection['ids'])
                raw = b''.join((json.dumps(event) + '\n').encode() for event in altered)
                blob = gzip.compress(raw, mtime=0)
                altered_path.write_bytes(blob)
                status_path = altered_path.parent / 'status.json'
                modified_status = json.loads(status_path.read_text())
                modified_status.update(gzip_sha256=hashlib.sha256(blob).hexdigest(),
                                       uncompressed_sha256=hashlib.sha256(raw).hexdigest())
                status_path.write_text(json.dumps(modified_status))
                with patch.object(sys, 'argv', ['audit_matched_proteins.py', str(all_output), '--allow-partial-development']), \
                     self.assertRaisesRegex(ValueError, 'Selection ranking mismatch'):
                    audit_main()
                failed_output = root / 'failed'
                failed_argv = ['run_matched_proteins.py', str(failed_output), '--dataset', 'ired', '--seeds', '7',
                               '--methods', 'random', '--specification', str(spec)]
                with patch.object(sys, 'argv', failed_argv), patch('run_matched_proteins.run_one', side_effect=RuntimeError), \
                     self.assertRaises(SystemExit):
                    main()
                status = json.loads((failed_output / 'seed_07/random/status.json').read_text())
                self.assertEqual((status['status'], status['error_type']), ('failed', 'RuntimeError'))
                with patch.object(sys, 'argv', failed_argv + ['--resume']), \
                     patch('run_matched_proteins.run_one') as retry, self.assertRaises(SystemExit):
                    main()
                retry.assert_not_called()
                failed_report = root / 'failed_report.json'
                with patch.object(sys, 'argv', ['evaluate_matched_proteins.py', str(failed_report), str(failed_output),
                                               '--specification', str(spec), '--allow-partial-development']):
                    evaluate_main()
                self.assertEqual(json.loads(failed_report.read_text())['groups'][0]['summaries'][0]['status'], 'failed')
                failed_status_path = failed_output / 'seed_07/random/status.json'
                failed_status_path.write_text(json.dumps({'status': 'interrupted'}))
                interrupted_report = root / 'interrupted_report.json'
                with patch.object(sys, 'argv', ['evaluate_matched_proteins.py', str(interrupted_report), str(failed_output),
                                               '--specification', str(spec), '--allow-partial-development']):
                    evaluate_main()
                self.assertEqual(json.loads(interrupted_report.read_text())['groups'][0]['summaries'][0]['status'], 'interrupted')


    def test_synthetic_hydro_evaluation_and_audit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, reference, spec, output = (root / name for name in ('data.csv', 'reference.fasta', 'spec.json', 'runs'))
            reference.write_text('>synthetic\n' + 'A' * 57 + '\n')
            sequences = ['A' * 55 + a + b for a, b in itertools.islice(
                itertools.product('ACDEFGHIKLMNPQRSTVWY', repeat=2), 120)]
            with data.open('w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['sequence', 'target', 'set', 'validation'])
                writer.writerows((sequence, index / 100, 'train' if index < 110 else 'test', 'False')
                                 for index, sequence in enumerate(sequences))
            spec.write_text(json.dumps(DEFAULT_SPEC))
            vectors = {sequence_id(sequence): np.asarray([i / 120, (i % 19) / 19], dtype=np.float32)
                       for i, sequence in enumerate(sequences)}
            argv = ['run_matched_proteins.py', str(output), '--dataset', 'hydro-P06241', '--seeds', '7',
                    '--methods', 'random', 'greedy', '--specification', str(spec)]
            with patch('app.datasets.hydro.DATA', data), patch.dict('app.datasets.hydro.REFERENCES', {'P06241': reference}), \
                 patch('app.features.hydro_representations.load_verified_representations', return_value=vectors), \
                 patch.object(sys, 'argv', argv):
                main()
                report = root / 'report.json'
                with patch.object(sys, 'argv', ['evaluate_matched_proteins.py', str(report), str(output),
                                               '--specification', str(spec), '--allow-partial-development']):
                    evaluate_main()
                group = json.loads(report.read_text())['groups'][0]
                self.assertEqual(group['dataset'], 'hydro-P06241')
                self.assertEqual([row['status'] for row in group['summaries']], ['completed', 'completed'])
                with patch.object(sys, 'argv', ['audit_matched_proteins.py', str(output), '--allow-partial-development']), \
                     redirect_stdout(io.StringIO()) as audit_output:
                    audit_main()
                self.assertEqual(json.loads(audit_output.getvalue())['groups'][0]['completed'], 2)


if __name__ == '__main__':
    unittest.main()
