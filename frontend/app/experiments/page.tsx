import { ArrowUpRight } from 'lucide-react';
import { ResultsTable } from '../../components/results-table';
import { ResultsLens } from '../../components/results-lens';
import { RESEARCH_SOURCE, SNAPSHOT_DATE } from '../../lib/research';

export const metadata={title:'Results'};
export default function Experiments(){
  return <div className="route-content">
    <header className="route-hero">
      <h1>Amylase results</h1>
      <p>Nine search methods, ten matched seeds. Retrospective development study, {SNAPSHOT_DATE.toLowerCase()}.</p>
    </header>
    <div className="evidence-stats" aria-label="Study summary">
      <div><span>Runs</span><strong>90</strong></div>
      <div><span>Selections</span><strong>658</strong></div>
      <div><span>Repair replays</span><strong>120</strong></div>
      <div><span>Accepted repairs</span><strong>0</strong></div>
    </div>
    <ResultsLens/>
    <ResultsTable/>
    <section className="result-notes">
      <h2>What happened</h2>
      <div>
        <p>Both repair methods stopped after 20 new measurements in every seed. None of the proposed changes passed the verifier.</p>
        <p>Recombination reached the highest measured eligible fitness in eight of ten runs. All initial sets already contained a top-1% candidate, making that metric uninformative here.</p>
        <p>These results are specific to amylase. Evaluation on IRED and hydrophobic-core proteins is pending.</p>
      </div>
    </section>
    <div className="source-row"><span>Full methodology, limitations and audit records</span>
      <a href={RESEARCH_SOURCE} target="_blank" rel="noreferrer" className="inline-link">Research report <ArrowUpRight size={17}/></a>
    </div>
    <footer className="site-footer"><span>CERA</span><a href={RESEARCH_SOURCE} target="_blank" rel="noreferrer">Source <ArrowUpRight size={14}/></a></footer>
  </div>;
}
