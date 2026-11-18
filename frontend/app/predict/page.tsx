import { Topbar } from '../../components/topbar';
import { PredictionForm } from './prediction-form';

export const metadata = { title: 'Predict' };
export default function Predict() {
  return (
    <>
      <Topbar section="Predict" />
      <div className="content route-content">
        <header className="route-header">
          <h1>
            Explore a<br />
            prediction.
          </h1>
          <p>Use the saved Amylase development model to estimate a score for an Amylase sequence.</p>
        </header>
        <div className="workflow-layout">
          <section className="results-section">
            <PredictionForm />
          </section>
          <aside className="method-note">
            <h2>What this means</h2>
            <p>
              A sequence is the chain of amino-acid letters that describes a protein. The model estimates its
              measured activity from a numerical representation of that chain.
            </p>
            <p>
              This tool accepts Amylase sequences with up to four changes from the reference. New sequences
              use the locally installed, verified representation model. Measured scores are not shown.
            </p>
          </aside>
        </div>
      </div>
    </>
  );
}
