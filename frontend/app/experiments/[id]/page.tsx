import Link from 'next/link';
import { notFound } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { Topbar } from '../../../components/topbar';
import { datasetName } from '../../../lib/experiment-datasets';
import { getRunReview } from '../../../lib/experiments';

export const metadata = { title: 'Experiment review' };
export const dynamic = 'force-dynamic';
const words = (value: string) => value.replaceAll('_', ' ');

export default async function ExperimentReview({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!/^[0-9a-f]{32}$/.test(id)) notFound();
  const { review, unavailable } = await getRunReview(id);
  if (!review && !unavailable) notFound();
  return <><Topbar section="Experiment review"/><div className="content route-content"><Link className="back-link" href="/experiments"><ArrowLeft size={15} aria-hidden="true"/> All experiments</Link>
    {!review ? <div className="offline"><strong>Experiment review unavailable</strong><p>The backend is unavailable, or the saved record could not be verified.</p></div> : <div className="workflow-layout"><section className="results-section">
      <span className="section-index">RECORDED LOCAL EXPERIMENT</span><h1>{datasetName(review.summary.dataset)}</h1><p>Seed {review.summary.seed} · {review.summary.gemini ? 'Gemini-assisted repair' : review.summary.repair ? 'Rule-based repair' : 'Fixed reward'} · {review.summary.new_measurements} new measurements · {review.summary.predictor === 'mixed' ? `mixed predictor (${review.summary.device === 'cuda' ? 'GPU' : 'CPU'})` : 'five ridge models'}</p>
      {review.goal && <p>Saved goal: {review.goal}</p>}<p>Reward weights: uncertainty {review.specification.terms.uncertainty_penalty.weight}, distance {review.specification.terms.distance_penalty.weight}, diversity {review.specification.terms.diversity_bonus.weight}.</p>
      <p>Best observed score: <strong>{review.summary.best_observed.toFixed(4)}</strong>. Stop reason: {words(review.summary.stop_reason)}.</p>
      <section className="batch-list"><h2>Batch history</h2><p>Each batch shows only variants selected and revealed in this run. The identifier is a fingerprint of the protein sequence.</p>{review.batches.map(batch => <details key={batch.round}><summary>Batch {batch.round} · {batch.measurements.length} measurements</summary>
        <div className="batch-body"><p><strong>Warnings:</strong> {batch.warnings.map(w => `${words(w.type)}: ${words(w.status)}`).join('; ') || 'none recorded'}</p>
          {batch.repairs.length > 0 && <div><h3>Repair decisions</h3>{batch.repairs.map((repair, index) => <div className="repair-record" key={index}><p>{words(repair.warning)}: <strong>{words(repair.status)}</strong>{repair.advice_source ? ` · advice: ${words(repair.advice_source)}` : ''}</p>{repair.attempts.length > 0 && <ul>{repair.attempts.map((attempt, n) => <li key={n}>{words(attempt.term)} → {attempt.proposed_weight}: {attempt.accepted ? 'accepted' : 'not accepted'}<ul>{Object.entries(attempt.checks).map(([name, passed]) => <li key={name}>{words(name)}: {passed === null ? 'unavailable' : passed ? 'passed' : 'failed'}</li>)}</ul></li>)}</ul>}</div>)}</div>}
          <div className="results-table-wrap" role="region" aria-label={`Measurements in batch ${batch.round}`} tabIndex={0}><table className="results-table batch-table"><caption>Selected and revealed variants</caption><thead><tr><th scope="col">Sequence fingerprint</th><th scope="col">Measured score</th><th scope="col">Prediction</th><th scope="col">Prediction range</th></tr></thead><tbody>{batch.measurements.map(row => <tr key={row.id}><th scope="row">{row.id}</th><td>{row.score.toFixed(4)}</td><td>{row.prediction.toFixed(4)}</td><td>{row.lower.toFixed(4)} to {row.upper.toFixed(4)}</td></tr>)}</tbody></table></div>
        </div></details>)}</section>
    </section><aside className="method-note"><h2>Reading this record</h2><p>The backend checks the saved measurements, timing of selections, dataset fingerprint and summary before showing this page. It does not independently refit each model or prove that a warning is scientifically valid.</p><p>These are retrospective simulations, not new laboratory measurements. Prediction ranges are estimates, not guarantees.</p><p>Run ID: {id}</p></aside></div>}
  </div></>;
}
