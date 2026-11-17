import Link from 'next/link';
import { Topbar } from '../../components/topbar';
import { getRecentExperiments } from '../../lib/experiments';
import { ExperimentForm } from './experiment-form';
import { datasetName } from '../../lib/experiment-datasets';
import { getGoals } from '../../lib/goals';

export const metadata = { title: 'Experiments' };
export const dynamic = 'force-dynamic';
export default async function Experiments() {
  const [runs, goals] = await Promise.all([getRecentExperiments(), getGoals()]);
  return <><Topbar section="Experiments"/><div className="content route-content"><header className="route-header"><h1>Run a local<br/><em>search.</em></h1><p>Simulate a search over previously measured protein variants. The search reveals a score only after choosing a variant.</p></header><div className="workflow-layout"><section className="results-section"><ExperimentForm goals={goals}/><section className="recent-runs"><h2>Recent local runs</h2>{runs === null ? <p>The backend is unavailable. Start it locally to see saved runs.</p> : runs.length === 0 ? <p>No local runs yet.</p> : <ul>{runs.map(run => <li key={run.id}>{run.status === 'completed' ? <><Link className="text-link" prefetch={false} href={`/experiments/${run.id}`}>{datasetName(run.dataset)} · Seed {run.seed} · {run.gemini ? 'Gemini-assisted repair' : run.repair ? 'Rule-based repair' : 'Fixed reward'}</Link><span>{run.new_measurements} new measurements · best {run.best_observed.toFixed(4)} · {run.predictor === 'mixed' ? `mixed (${run.device === 'cuda' ? 'GPU' : 'CPU'})` : 'five ridge models'}</span></> : <><strong>Incomplete or running</strong><span>Check backend logs and saved record before retrying.</span></>}<small>{run.id}</small></li>)}</ul>}</section></section><aside className="method-note"><h2>Before you run</h2><p>This is a retrospective simulation, not a laboratory measurement. Only one local experiment can run at a time; saved records are never overwritten.</p><p>Choose the fixed specification or a saved, reviewed goal. Gemini is called only when you select Gemini-assisted repair; requests may incur charges. It is intended for a local workspace, not a publicly deployed service.</p></aside></div></div></>;
}
