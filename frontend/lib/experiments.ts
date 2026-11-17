import 'server-only';

export type Experiment = { id: string; seed: number; repair: boolean; new_measurements: number; best_observed: number; stop_reason: string; covered: number | null; range_count: number; mean_range_width: number | null; warnings: Record<string, number>; accepted_repairs: number };
export type RecentExperiment = ({ status: 'completed' } & Experiment) | { status: 'incomplete_or_running'; id: string };
export async function getRecentExperiments(): Promise<RecentExperiment[] | null> {
  try {
    const response = await fetch(`${process.env.CERA_API_URL || 'http://127.0.0.1:8000'}/api/experiments/amylase`, { cache: 'no-store', signal: AbortSignal.timeout(3000) });
    return response.ok ? await response.json() as RecentExperiment[] : null;
  } catch { return null; }
}
