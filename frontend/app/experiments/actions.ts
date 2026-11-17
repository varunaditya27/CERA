'use server';
import { revalidatePath } from 'next/cache';
import type { Experiment } from '../../lib/experiments';
import { experimentDatasets } from '../../lib/experiment-datasets';

export type ExperimentState = { result?: Experiment; error?: string };
export async function startExperiment(_: ExperimentState, form: FormData): Promise<ExperimentState> {
  const raw = form.get('seed');
  const method = form.get('method');
  const dataset = form.get('dataset');
  const goal = form.get('goal');
  if (typeof goal !== 'string' || (goal !== 'default' && !/^[0-9a-f]{32}:[0-9a-f]{64}$/.test(goal))) return { error: 'Choose a valid saved goal.' };
  const [goalId, goalSha] = goal === 'default' ? [null, null] : goal.split(':');
  if (typeof dataset !== 'string' || !Object.hasOwn(experimentDatasets, dataset) || typeof raw !== 'string' || !/^\d{1,10}$/.test(raw) || Number(raw) > 2147483647 || !['fixed', 'repair', 'gemini'].includes(String(method))) return { error: 'Enter a whole-number seed from 0 to 2,147,483,647 and choose a method.' };
  try {
    const response = await fetch(`${process.env.CERA_API_URL || 'http://127.0.0.1:8000'}/api/experiments/${encodeURIComponent(dataset)}`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ seed: Number(raw), repair: method !== 'fixed', gemini: method === 'gemini', goal_id: goalId, goal_sha256: goalSha }), cache: 'no-store', signal: AbortSignal.timeout(120000),
    });
    revalidatePath('/experiments');
    if (response.status === 503) return { error: 'Gemini is not configured. Check the API key and model in backend/.env.' };
    if (response.status === 409) {
      const body = await response.json();
      return { error: body.detail === 'Saved goal is missing or has changed.' ? 'The saved goal changed or is missing. Review it again before running.' : 'Another local experiment is already running. Wait for it to finish.' };
    }
    if (!response.ok) return { error: 'The experiment did not complete. Check recent runs and backend logs for a partial record.' };
    return { result: await response.json() as Experiment };
  } catch {
    revalidatePath('/experiments');
    return { error: 'The backend did not respond. The run may still be active; check recent runs before starting another.' };
  }
}
