'use server';

type Prediction = { mean: number; lower: number; upper: number; observed_role: 'fitting' | 'range_setting' | 'unobserved_in_episode'; representation_source: 'cache' | 'generated' };
export type PredictionState = { result?: Prediction; error?: string };

export async function predict(_: PredictionState, form: FormData): Promise<PredictionState> {
  const sequence = form.get('sequence');
  if (typeof sequence !== 'string' || !sequence.trim() || sequence.length > 1000) return { error: 'Enter an Amylase sequence of no more than 1,000 letters.' };
  try {
    const response = await fetch(`${process.env.CERA_API_URL || 'http://127.0.0.1:8000'}/api/predictions/amylase`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ sequence }), signal: AbortSignal.timeout(60000), cache: 'no-store',
    });
    if (response.status === 422) return { error: 'Use standard amino-acid letters and the Amylase reference length, with no more than four changes.' };
    if (!response.ok) return { error: 'The model or verified sequence representations are unavailable.' };
    const result = await response.json() as Prediction;
    if (![result.mean, result.lower, result.upper].every(Number.isFinite) || result.lower > result.mean || result.mean > result.upper || !['fitting', 'range_setting', 'unobserved_in_episode'].includes(result.observed_role) || !['cache', 'generated'].includes(result.representation_source)) throw new Error('Invalid prediction');
    return { result };
  } catch { return { error: 'The prediction service is unavailable. Check that the backend is running.' }; }
}
