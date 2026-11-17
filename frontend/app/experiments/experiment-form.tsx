'use client';
import { useActionState } from 'react';
import Link from 'next/link';
import type { SavedGoal } from '../../lib/goals';
import { startExperiment } from './actions';
import { datasetName, experimentDatasets } from '../../lib/experiment-datasets';

export function ExperimentForm({ goals }: { goals: SavedGoal[] | null }) {
  const [state, action, pending] = useActionState(startExperiment, {});
  return <><form action={action} className="experiment-form">
    <label htmlFor="dataset">Protein dataset</label><p id="dataset-help">Each hydrophobic-core protein is a separate search.</p><select id="dataset" name="dataset" defaultValue="amylase" aria-describedby="dataset-help">{Object.entries(experimentDatasets).map(([id, name]) => <option value={id} key={id}>{name}</option>)}</select>
    <label htmlFor="goal">Reward specification</label><p id="goal-choice-help">Use the fixed default or select a saved goal after reviewing its weights on the <Link className="text-link" href="/goals">Goals page</Link>. {goals === null && 'Saved goals are unavailable.'}</p><select id="goal" name="goal" defaultValue="default" aria-describedby="goal-choice-help"><option value="default">Fixed default specification</option>{goals?.map(goal => <option key={goal.id} value={`${goal.id}:${goal.sha256}`}>{goal.input_goal.slice(0, 80)} · {goal.id.slice(0, 8)}</option>)}</select>
    <label htmlFor="seed">Starting seed</label><p id="seed-help">A whole number controls the initial sample. Use the same seed to reproduce the starting examples.</p>
    <input id="seed" name="seed" type="number" defaultValue="1" min="0" max="2147483647" step="1" required aria-describedby="seed-help"/>
    <fieldset><legend>Search method</legend><label><input type="radio" name="method" value="fixed" defaultChecked/> Fixed reward</label><label><input type="radio" name="method" value="repair"/> Rule-based repair</label><label><input type="radio" name="method" value="gemini"/> Gemini-assisted repair</label></fieldset>
    <p>Starting examples come from the dataset’s training group; later choices may come from all eligible variants. Hydrophobic-core training membership was defined using measured fitness, so it is not a blind start.</p><p>All methods use five ridge predictors and at most 100 new simulated measurements. Repair can stop early if checks fail. Gemini may make billable API requests and can fall back to a local choice if unavailable; only warning types and repair options are sent.</p>
    <button type="submit" className="primary-link" disabled={pending}>{pending ? 'Running experiment…' : 'Run local experiment'}</button>
  </form><div className="prediction-output" aria-live="polite" aria-atomic="true">
    {state.error && <p className="prediction-error">{state.error}</p>}
    {state.result && <section aria-labelledby="run-result"><h2 id="run-result">Completed experiment</h2><p>{datasetName(state.result.dataset)} · Seed {state.result.seed} · {state.result.gemini ? 'Gemini-assisted repair' : state.result.repair ? 'Rule-based repair' : 'Fixed reward'}</p><dl><div><dt>New measurements</dt><dd>{state.result.new_measurements}</dd></div><div><dt>Best observed score</dt><dd>{state.result.best_observed.toFixed(4)}</dd></div><div><dt>Scores inside predicted ranges</dt><dd>{state.result.covered ?? 'Unavailable'} / {state.result.range_count}</dd></div><div><dt>Accepted repairs</dt><dd>{state.result.accepted_repairs}</dd></div></dl>{state.result.gemini && <p>Provider request attempts: {state.result.provider_attempts}; fallbacks: {state.result.provider_fallbacks}. Known reported tokens: {state.result.reported_total_tokens ?? 'unavailable'} across {state.result.provider_usage_reports ?? 0} attempts. Token counts are not a billing total.</p>}<p>Triggered warnings: {Object.entries(state.result.warnings).length ? Object.entries(state.result.warnings).map(([name, count]) => `${name.replaceAll('_', ' ')}: ${count}`).join('; ') : 'none'}.</p><p>Stop reason: {state.result.stop_reason.replaceAll('_', ' ')}. Run ID: {state.result.id}</p></section>}
  </div></>;
}
