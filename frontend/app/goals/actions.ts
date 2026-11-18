'use server';
import { revalidatePath } from 'next/cache';
import type { SavedGoal } from '../../lib/goals';

export type GoalState = { goal?: SavedGoal; error?: string };
export async function compileGoal(_: GoalState, form: FormData): Promise<GoalState> {
  const goal = form.get('goal');
  if (typeof goal !== 'string' || !goal.trim() || goal.length > 1000)
    return { error: 'Enter a goal of up to 1,000 characters.' };
  try {
    const response = await fetch(`${process.env.CERA_API_URL || 'http://127.0.0.1:8000'}/api/goals`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ goal }),
      cache: 'no-store',
      signal: AbortSignal.timeout(100000),
    });
    revalidatePath('/goals');
    revalidatePath('/experiments');
    if (response.status === 422)
      return {
        error:
          'This goal could not be represented by the supported fitness search. Try a fitness-maximization goal without changing its fixed limits.',
      };
    if (response.status === 503)
      return { error: 'Gemini is not configured. Check the API key and model in backend/.env.' };
    if (!response.ok) return { error: 'Gemini could not produce a valid specification. No goal was saved.' };
    return { goal: (await response.json()) as SavedGoal };
  } catch {
    return {
      error: 'The backend did not respond. Check saved goals before retrying; the request may still finish.',
    };
  }
}
