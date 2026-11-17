'use client';
import { useActionState, useState } from 'react';
import { predict } from './actions';

const roleText = {
  fitting: 'This sequence was used to fit the model.',
  range_setting: 'This sequence was used to set the prediction range.',
  unobserved_in_episode: 'This sequence was not observed in the original search episode.',
};

export function PredictionForm() {
  const [state, action, pending] = useActionState(predict, {});
  const [sequence, setSequence] = useState('');
  const [submitted, setSubmitted] = useState('');
  const showResult = !pending && sequence === submitted;
  return <><form action={action} className="prediction-form" onSubmit={() => setSubmitted(sequence)}>
    <label htmlFor="sequence">Amylase amino-acid sequence <span>(required)</span></label>
    <p id="sequence-help">Paste the complete sequence as letters without spaces. It must be in the verified dataset cache and differ from the reference by no more than four amino acids.</p>
    <textarea id="sequence" name="sequence" required maxLength={1000} rows={7} spellCheck={false} autoCapitalize="none" autoCorrect="off" aria-describedby="sequence-help" value={sequence} onChange={event => setSequence(event.target.value)}/>
    <button className="primary-link" type="submit" disabled={pending}>{pending ? 'Calculating…' : 'Calculate prediction'}</button>
  </form><div aria-live="polite" aria-atomic="true" className="prediction-output">
    {showResult && state.error && <p className="prediction-error">{state.error}</p>}
    {showResult && state.result && <section aria-labelledby="prediction-heading"><h2 id="prediction-heading">Model prediction</h2><dl><div><dt>Predicted score</dt><dd>{state.result.mean.toFixed(4)}</dd></div><div><dt>Prediction range</dt><dd>{state.result.lower.toFixed(4)} to {state.result.upper.toFixed(4)}</dd></div></dl><p>{roleText[state.result.observed_role]}</p><p>The range is an estimate, not a guarantee. This development model is not validated for laboratory decisions.</p></section>}
  </div></>;
}
