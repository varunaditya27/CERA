import { ArrowUpRight } from 'lucide-react';
import { Topbar } from '../../components/topbar';
import { ResultsTable } from '../../components/results-table';
import { RESEARCH_SOURCE, SNAPSHOT_DATE } from '../../lib/research';

export const metadata={title:'Results'};
export default function Experiments(){
 return <><Topbar section="Results"/><div className="route-content">
   <header className="route-hero"><h1>Amylase results</h1><p>Nine search methods compared across ten matched seeds. Retrospective development study, {SNAPSHOT_DATE.toLowerCase()}.</p></header>
   <div className="evidence-stats" aria-label="Study summary">
     <div><span>Runs</span><strong>90</strong></div>
     <div><span>Selections</span><strong>658</strong></div>
     <div><span>Repair replays</span><strong>120</strong></div>
     <div><span>Accepted repairs</span><strong>0</strong></div>
   </div>
   <ResultsTable/>
   <section className="result-notes">
     <div><h2>What happened</h2></div>
     <div><p>Both repair methods stopped after 20 new measurements in every seed because none of the proposed changes passed the verifier.</p><p>Recombination reached the best eligible measured score in eight of ten runs. All initial sets already contained a top-1% candidate, so that measure cannot distinguish methods.</p><p>These findings are specific to the amylase development pool. IRED and hydrophobic-core evaluations are still pending.</p></div>
   </section>
   <div className="source-row"><span>Full methods, limitations, and audit records</span><a href={RESEARCH_SOURCE} target="_blank" rel="noreferrer" className="inline-link">Research report <ArrowUpRight size={17}/></a></div>
   <footer className="site-footer"><span>CERA</span><a href={RESEARCH_SOURCE} target="_blank" rel="noreferrer">Source <ArrowUpRight size={14}/></a></footer>
 </div></>;
}
