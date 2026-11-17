'use client';
import { useActionState, useState } from 'react';
import { compileGoal } from './actions';

export function GoalForm() {
  const [state, action, pending] = useActionState(compileGoal, {});
  const [text, setText] = useState('');
  const [submitted, setSubmitted] = useState('');
  const current = !pending && text === submitted;
  return <><form className="prediction-form" action={action} onSubmit={() => setSubmitted(text)}>
    <label htmlFor="goal">Fitness search goal <span>(required)</span></label>
    <p id="goal-help">The only supported objective is maximizing the dataset fitness score. The budget and mutation limit are fixed. Your text is sent to Google Gemini and saved locally; do not include secrets or information you do not want to share. API calls may incur charges.</p>
    <textarea id="goal" name="goal" required maxLength={1000} rows={5} aria-describedby="goal-help" value={text} onChange={event => setText(event.target.value)}/>
    <button type="submit" className="primary-link" disabled={pending}>{pending ? 'Compiling goal…' : 'Compile goal with Gemini'}</button>
  </form><div className="prediction-output" aria-live="polite" aria-atomic="true">{current && state.error && <p className="prediction-error">{state.error}</p>}{current && state.goal && <p>Goal saved. Review its weights below before selecting it for an experiment.</p>}</div></>;
}
