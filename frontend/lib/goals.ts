import 'server-only';

export type SavedGoal = { id: string; sha256: string; input_goal: string; model: string; specification: { terms: Record<'uncertainty_penalty' | 'distance_penalty' | 'diversity_bonus', { weight: number }>; budget: { rounds: number; batch_size: number }; hard_constraints: { max_mutations: number } } };
export async function getGoals(): Promise<SavedGoal[] | null> {
  try {
    const response = await fetch(`${process.env.CERA_API_URL || 'http://127.0.0.1:8000'}/api/goals`, { cache: 'no-store', signal: AbortSignal.timeout(3000) });
    return response.ok ? await response.json() as SavedGoal[] : null;
  } catch { return null; }
}
