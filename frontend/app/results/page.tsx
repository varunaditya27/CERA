import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import { Topbar } from '../../components/topbar';
import { getMixedSearchResults } from '../../lib/results';
import { BarRows } from '../../components/bar-rows';
import { PrimaryStudy } from './primary-study';

export const metadata = { title: 'Results' };
export const dynamic = 'force-dynamic';

export default async function Results() {
  const result = await getMixedSearchResults();
  return (
    <>
      <Topbar section="Results" />
      <div className="content route-content">
        <header className="route-header">
          <h1>
            What the search
            <br />
            found.
          </h1>
          <p>Recorded results from simulated searches over previously measured protein variants.</p>
        </header>
        <PrimaryStudy />
        {result ? (
          <div className="workflow-layout">
            <section className="results-section">
              <span className="section-index">Amylase development study</span>
              <h2>Two predictors, matched starts</h2>
              <p>
                Each method began with the same measured examples in {result.pairs} paired searches and could
                measure 100 more variants. The mixed group combines three ridge models and two neural
                networks; the comparison uses five ridge models.
              </p>
              <div className="results-highlight">
                <strong>
                  {result.ties} of {result.pairs}
                </strong>
                <span>pairs ended with the same best score</span>
              </div>
              <p>
                Mixed scored higher in {result.mixed_higher} pairs; five ridge models scored higher in{' '}
                {result.ridge_higher}. The methods could select different variants, so a tie does not
                establish equivalence.
              </p>
              <BarRows
                id="coverage-chart"
                title="Scores inside the predicted range"
                description={`Of the ${result.methods.mixed.measured} scores each method selected, ${result.methods.mixed.covered} fell inside the mixed group's range and ${result.methods.ridge.covered} inside the five-ridge range. The table below gives the same counts.`}
                rows={[
                  {
                    label: 'Mixed group',
                    segments: [
                      { value: result.methods.mixed.covered, tone: 'accent', label: 'Inside range' },
                      {
                        value: result.methods.mixed.measured - result.methods.mixed.covered,
                        tone: 'rest',
                        label: 'Outside range',
                      },
                    ],
                  },
                  {
                    label: 'Five ridge',
                    segments: [
                      { value: result.methods.ridge.covered, tone: 'accent', label: 'Inside range' },
                      {
                        value: result.methods.ridge.measured - result.methods.ridge.covered,
                        tone: 'rest',
                        label: 'Outside range',
                      },
                    ],
                  },
                ]}
                legend={[
                  { tone: 'accent', label: 'Inside range' },
                  { tone: 'rest', label: 'Outside range' },
                ]}
              />
              <div
                className="results-table-wrap"
                role="region"
                aria-labelledby="results-caption"
                tabIndex={0}
              >
                <table className="results-table">
                  <caption id="results-caption">Selected measurements and run time</caption>
                  <thead>
                    <tr>
                      <th scope="col">Measure</th>
                      <th scope="col">Mixed group</th>
                      <th scope="col">Five ridge</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <th scope="row">Scores inside predicted range</th>
                      <td>
                        {result.methods.mixed.covered} / {result.methods.mixed.measured}
                      </td>
                      <td>
                        {result.methods.ridge.covered} / {result.methods.ridge.measured}
                      </td>
                    </tr>
                    <tr>
                      <th scope="row">Average range width</th>
                      <td>{result.methods.mixed.mean_width.toFixed(3)}</td>
                      <td>{result.methods.ridge.mean_width.toFixed(3)}</td>
                    </tr>
                    <tr>
                      <th scope="row">Average run time</th>
                      <td>{result.methods.mixed.mean_seconds.toFixed(2)} sec</td>
                      <td>{result.methods.ridge.mean_seconds.toFixed(2)} sec</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <p>
                Range coverage describes the scores each method selected. Run time includes the full episode
                on this machine and is not a portable speed benchmark.
              </p>
            </section>
            <aside className="method-note">
              <span className="section-index">How to read this</span>
              <h2>Evidence, with limits.</h2>
              <p>
                These are retrospective simulations on one development dataset, not new laboratory
                experiments. One audit replayed all 200 selections. A later audit rebuilt all 100
                mixed-predictor rounds on the same GPU and reproduced the recorded predictions.
              </p>
              <p>
                Results do not establish generalization to other proteins or the effect of reward repair. Use
                Experiments to run a local simulation. The project scripts reproduce the wider studies.
              </p>
              <Link className="text-link" href="/experiments">
                Open experiments <ArrowRight size={16} aria-hidden="true" />
              </Link>
            </aside>
          </div>
        ) : (
          <div className="offline">
            <strong>Amylase comparison unavailable</strong>
            <p>Start the backend and check that the saved Amylase audit is present.</p>
          </div>
        )}
      </div>
    </>
  );
}
