import { Topbar } from '../../components/topbar';
import { getRecentExperiments } from '../../lib/experiments';
import { ExperimentForm } from './experiment-form';

export const metadata = { title: 'Experiments' };
export const dynamic = 'force-dynamic';
export default async function Experiments() {
  const runs = await getRecentExperiments();
  return <><Topbar section="Experiments"/><div className="content route-content"><header className="route-header"><h1>Run a local<br/><em>search.</em></h1><p>Simulate a search over previously measured Amylase variants. The search reveals a score only after choosing a variant.</p></header><div className="workflow-layout"><section className="results-section"><ExperimentForm/><section className="recent-runs"><h2>Recent local runs</h2>{runs === null ? <p>The backend is unavailable. Start it locally to see saved runs.</p> : runs.length === 0 ? <p>No local runs yet.</p> : <ul>{runs.map(run => <li key={run.id}>{run.status === 'completed' ? <><strong>Seed {run.seed} · {run.repair ? 'Rule-based repair' : 'Fixed reward'}</strong><span>{run.new_measurements} new measurements · best {run.best_observed.toFixed(4)}</span></> : <><strong>Incomplete or running</strong><span>Check backend logs and saved record before retrying.</span></>}<small>{run.id}</small></li>)}</ul>}</section></section><aside className="method-note"><h2>Before you run</h2><p>This is a retrospective simulation, not a laboratory measurement. Only one local experiment can run at a time; saved records are never overwritten.</p><p>The web runner uses a fixed specification and does not call Gemini. It is intended for a local workspace, not a publicly deployed service.</p></aside></div></div></>;
}
