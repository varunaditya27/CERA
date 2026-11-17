import 'server-only';

export type Experiment = { id: string; dataset?: string; goal_id?: string | null; predictor?: 'ridge' | 'mixed'; device?: 'cpu' | 'cuda' | null; seed: number; repair: boolean; gemini?: boolean; provider_attempts?: number; provider_fallbacks?: number; reported_total_tokens?: number | null; provider_usage_reports?: number; new_measurements: number; best_observed: number; stop_reason: string; covered: number | null; range_count: number; mean_range_width: number | null; warnings: Record<string, number>; accepted_repairs: number };
export type RecentExperiment = ({ status: 'completed' } & Experiment) | { status: 'incomplete_or_running'; id: string };
export async function getRecentExperiments(): Promise<RecentExperiment[] | null> {
  try {
    const response = await fetch(`${process.env.CERA_API_URL || 'http://127.0.0.1:8000'}/api/experiments`, { cache: 'no-store', signal: AbortSignal.timeout(3000) });
    return response.ok ? await response.json() as RecentExperiment[] : null;
  } catch { return null; }
}

type Attempt = { term: string; proposed_weight: number; accepted: boolean; checks: Record<string, boolean | null> };
type Repair = { warning: string; status: string; advice_source: string | null; attempts: Attempt[] };
type Batch = { round: number; measurements: { id: string; score: number; prediction: number; lower: number; upper: number }[]; warnings: { type: string; status: string }[]; repairs: Repair[] };
export type RunReview = { summary: Experiment; batches: Batch[]; goal: string | null; specification: { terms: Record<'uncertainty_penalty' | 'distance_penalty' | 'diversity_bonus', { weight: number }> } };
export async function getRunReview(id: string): Promise<{ review?: RunReview; unavailable: boolean }> {
  try {
    const response = await fetch(`${process.env.CERA_API_URL || 'http://127.0.0.1:8000'}/api/experiments/run/${encodeURIComponent(id)}/review`, { cache: 'no-store', signal: AbortSignal.timeout(15000) });
    if (response.status === 404) return { unavailable: false };
    if (!response.ok) return { unavailable: true };
    return { review: await response.json() as RunReview, unavailable: false };
  } catch { return { unavailable: true }; }
}
