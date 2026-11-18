import Link from 'next/link';
import { notFound } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { Topbar } from '../../../../components/topbar';
import { getDecisionAudit } from '../../../../lib/experiments';

export const metadata = { title: 'Decision check' };
export const dynamic = 'force-dynamic';
export default async function DecisionAudit({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  if (!/^[0-9a-f]{32}$/.test(id)) notFound();
  const { audit, unavailable } = await getDecisionAudit(id);
  if (!audit && !unavailable) notFound();
  return (
    <>
      <Topbar section="Decision check" />
      <div className="content route-content">
        <Link className="back-link" href={`/experiments/${id}`}>
          <ArrowLeft size={15} aria-hidden="true" /> Back to experiment
        </Link>
        <div className="workflow-layout">
          <section className="results-section">
            <h1>
              Check the
              <br />
              <em>decisions.</em>
            </h1>
            {audit ? (
              <>
                <div className="results-highlight">
                  <strong>Passed</strong>
                  <span>recorded selection and replay checks</span>
                </div>
                <p>
                  Checked {audit.selections_checked} batch selections and {audit.repair_replays_checked}{' '}
                  repair proposal replays. The check recomputed distances and rankings from the saved evidence
                  and verified the current code and representation cache fingerprints.
                </p>
                <p>Run ID: {id}</p>
              </>
            ) : (
              <div className="offline">
                <strong>Decision check unavailable</strong>
                <p>
                  The backend could not verify this record or its sources. The saved code or cache may have
                  changed, the record may be incomplete, or the backend may be unavailable. The check does not
                  alter the record.
                </p>
              </div>
            )}
          </section>
          <aside className="method-note">
            <h2>What this does not prove</h2>
            <p>
              The check uses recorded model predictions; it does not retrain the predictors. It replays the
              selected candidates and displacement check, but does not independently recompute every repair
              check or establish that a warning is biologically meaningful.
            </p>
            <p>Passing is an engineering consistency check, not evidence of scientific benefit.</p>
          </aside>
        </div>
      </div>
    </>
  );
}
