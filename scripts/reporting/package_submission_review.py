#!/usr/bin/env python3
"""Build the submission review ZIP from the current Git commit."""
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
DESTINATION = ROOT / 'output/packages/CERA-submission-review.zip'
PREFIX = 'CERA-review/'
FILES = (
    'README.md',
    'backend/app/rewards/repair_menu.py',
    'data/SOURCES.md',
    'docs/background/dataset_evidence_ledger.md',
    'docs/background/esm_feasibility.md',
    'docs/background/literature_review.md',
    'docs/college/Project_Briefing_Guide.pdf',
    'docs/college/Project_Synopsis.pdf',
    'docs/data/ired_preparation.md',
    'docs/explainers/datasets.html',
    'docs/history/work_log.md',
    'docs/overview/completion_review.md',
    'docs/overview/status_and_results.md',
    'docs/overview/submission_readiness.md',
    'docs/overview/workshop_draft.md',
    'docs/studies/amylase/position_shift.md',
    'docs/studies/amylase/prediction_ranges.md',
    'docs/studies/amylase/repeated_comparison.md',
    'docs/studies/hybrid/heldout_shift_prediction.md',
    'docs/studies/hybrid/hybrid_predictor.md',
    'docs/studies/hybrid/mixed_heldout.md',
    'docs/studies/hybrid/mixed_search_comparison.md',
    'docs/studies/hybrid/model_export.md',
    'docs/studies/multiprotein/additional_metrics.md',
    'docs/studies/multiprotein/four_protein_findings.md',
    'docs/studies/multiprotein/hydro_low_fitness.md',
    'docs/studies/multiprotein/hydro_repair_stopping.md',
    'docs/studies/multiprotein/ired_low_change.md',
    'docs/studies/multiprotein/paired_analysis.md',
    'docs/studies/repair/after_repair_coverage.md',
    'docs/studies/warnings/controlled_simulations.md',
    'docs/workspace/local_decision_audit.md',
    'output/heldout/amylase_position_shift_121_130.json',
    'output/warnings/coverage_warning_followup_regret.csv',
    'output/warnings/coverage_warning_simulation.json',
    'output/warnings/disagreement_warning_simulation.json',
    'output/heldout/heldout_shift_evaluation_121_130.json',
    'output/multiprotein/four_protein/matched_eval_51_60_audit_rerun.json',
    'output/multiprotein/four_protein/matched_eval_51_60_method_summary.csv',
    'output/multiprotein/four_protein/matched_eval_51_60_report.json',
    'output/multiprotein/four_protein/matched_eval_51_60_same_measurements.json',
    'output/hybrid/mixed_heldout_comparison_121_130.json',
    'output/hybrid/mixed_heldout_evaluation_121_130.json',
    'output/hybrid/mixed_search_comparison_191_200_audit.json',
    'output/warnings/rule_warning_controls.json',
    'output/warnings/support_warning_simulation.json',
    'presentation/project_review.html',
    'report/CERA_final_report.pdf',
    'report/CERA_final_report.tex',
)


def main():
    with TemporaryDirectory(dir=DESTINATION.parent) as directory:
        candidate = Path(directory) / DESTINATION.name
        subprocess.run(
            ['git', 'archive', '--format=zip', f'--prefix={PREFIX}', '-o', str(candidate), 'HEAD', '--', *FILES],
            cwd=ROOT, check=True,
        )
        with ZipFile(candidate) as archive:
            entries = sorted(item.filename for item in archive.infolist() if not item.is_dir())
            if entries != sorted(PREFIX + name for name in FILES) or archive.testzip() is not None:
                raise ValueError('Review archive has missing, unexpected, or damaged files')
        candidate.replace(DESTINATION)
    print(DESTINATION)


if __name__ == '__main__':
    main()
