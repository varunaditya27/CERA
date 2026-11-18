#!/usr/bin/env python3
"""Build the submission review ZIP from the current Git commit."""
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
DESTINATION = ROOT / 'output/CERA-submission-review.zip'
PREFIX = 'CERA-review/'
FILES = (
    'Project_Briefing_Guide.pdf',
    'Project_Synopsis.pdf',
    'README.md',
    'backend/app/rewards/repair_menu.py',
    'data/SOURCES.md',
    'datasets.html',
    'output/amylase_position_shift_121_130.json',
    'output/coverage_warning_followup_regret.csv',
    'output/coverage_warning_simulation.json',
    'output/disagreement_warning_simulation.json',
    'output/heldout_shift_evaluation_121_130.json',
    'output/matched_eval_51_60_audit_rerun.json',
    'output/matched_eval_51_60_method_summary.csv',
    'output/matched_eval_51_60_report.json',
    'output/matched_eval_51_60_same_measurements.json',
    'output/mixed_heldout_comparison_121_130.json',
    'output/mixed_heldout_evaluation_121_130.json',
    'output/mixed_search_comparison_191_200_audit.json',
    'output/pdf/CERA_final_report.pdf',
    'output/rule_warning_controls.json',
    'output/support_warning_simulation.json',
    'project_review.html',
    'research/CERA_final_report.tex',
    'research/additional_metrics_findings.md',
    'research/amylase_position_shift_findings.md',
    'research/after_repair_coverage_findings.md',
    'research/completion_evidence_review.md',
    'research/dataset_evidence_ledger.md',
    'research/disagreement_warning_simulation_findings.md',
    'research/esm_feasibility_and_plan.md',
    'research/exploratory_paired_analysis_findings.md',
    'research/heldout_shift_prediction_findings.md',
    'research/heldout_shift_prediction_protocol.md',
    'research/hybrid_model_export_findings.md',
    'research/hybrid_predictor_protocol.md',
    'research/hydro_low_fitness_search_findings.md',
    'research/hydro_repair_stopping_diagnosis_findings.md',
    'research/ired_low_change_findings.md',
    'research/ired_preparation.md',
    'research/literature_review.md',
    'research/local_decision_audit.md',
    'research/mixed_heldout_findings.md',
    'research/mixed_search_comparison_findings.md',
    'research/multiprotein_study_findings.md',
    'research/prediction_range_pilot_findings.md',
    'research/project_decisions_and_work_log.md',
    'research/project_status_and_results.md',
    'research/repeated_comparison_findings.md',
    'research/rule_warning_controls_findings.md',
    'research/submission_readiness.md',
    'research/workshop_draft.md',
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
