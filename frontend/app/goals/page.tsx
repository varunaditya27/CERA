import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import { Topbar } from '../../components/topbar';
import { getGoals } from '../../lib/goals';
import { GoalForm } from './goal-form';

export const metadata = { title: 'Goals' };
export const dynamic = 'force-dynamic';
export default async function Goals() {
  const goals = await getGoals();
  return (
    <>
      <Topbar section="Goals" />
      <div className="content route-content">
        <header className="route-header">
          <h1>
            Describe the
            <br />
            search.
          </h1>
          <p>
            Turn a fitness-maximization goal into a bounded specification, then review it before running an
            experiment.
          </p>
        </header>
        <div className="workflow-layout">
          <section className="results-section">
            <GoalForm />
            <section className="recent-runs">
              <h2>Saved goals</h2>
              {goals === null ? (
                <p>The backend is unavailable. Start it locally to review saved goals.</p>
              ) : goals.length === 0 ? (
                <p>No saved goals yet.</p>
              ) : (
                <ul>
                  {goals.map((goal) => (
                    <li key={goal.id}>
                      <strong>{goal.input_goal}</strong>
                      <span>
                        Uncertainty penalty {goal.specification.terms.uncertainty_penalty.weight}, distance
                        penalty {goal.specification.terms.distance_penalty.weight}, diversity bonus{' '}
                        {goal.specification.terms.diversity_bonus.weight}
                      </span>
                      <span>
                        Up to {goal.specification.hard_constraints.max_mutations} sequence changes;{' '}
                        {goal.specification.budget.rounds} batches of {goal.specification.budget.batch_size}.
                      </span>
                      <small>Goal ID: {goal.id}</small>
                    </li>
                  ))}
                </ul>
              )}
              <Link className="text-link" href="/experiments">
                Choose a goal for an experiment <ArrowRight size={16} aria-hidden="true" />
              </Link>
            </section>
          </section>
          <aside className="method-note">
            <h2>Review before running</h2>
            <p>
              Gemini may misunderstand your goal. The application checks the permitted values, but that does
              not prove the weights reflect your intent or improve results.
            </p>
            <p>
              The uncertainty and distance penalties discourage uncertain or unfamiliar candidates. The
              diversity bonus encourages differences within a batch.
            </p>
          </aside>
        </div>
      </div>
    </>
  );
}
