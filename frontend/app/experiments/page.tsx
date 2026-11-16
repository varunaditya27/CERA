import { ArrowUpRight, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { Topbar } from '../../components/topbar';
import { ResultsTable } from '../../components/results-table';
import { RESEARCH_SOURCE, SNAPSHOT_DATE } from '../../lib/research';

export const metadata={title:'Experiments'};

export default function Experiments() {
  return <><Topbar section="Experiments" eyebrow="DEVELOPMENT EVIDENCE"/>
    <div className="route-content">
      <header className="route-hero route-hero-wide"><p className="eyebrow">03 / EXPERIMENTAL EVIDENCE</p><div className="route-heading-grid"><h1>Evidence, <em>not promises.</em></h1><div><p>The latest committed comparison tests nine search policies under the same starting conditions. These are retrospective finite-pool development results on alpha amylase, not a final validation across proteins.</p><span className="meta-line">DATA SNAPSHOT / {SNAPSHOT_DATE} · 10 MATCHED SEEDS</span></div></div></header>
      <section className="evidence-stats" aria-label="Study summary">
        <div><span>SIMULATED RUNS</span><strong>90</strong><p>Ten seeds × nine methods</p></div>
        <div><span>RECORDED SELECTIONS</span><strong>658</strong><p>Independently audited in the repository</p></div>
        <div><span>REPAIR REPLAYS</span><strong>120</strong><p>No proposed change accepted</p></div>
        <div><span>POOL MAXIMUM</span><strong>0.21163</strong><p>Best measured eligible amylase score</p></div>
      </section>
      <ResultsTable/>
      <section className="evidence-interpretation" aria-label="Interpretation and limitations">
        <div className="interpretation-heading"><p className="eyebrow">WHAT THE RECORD SUPPORTS</p><h2>Read the result.<br/><em>Keep the caveats.</em></h2></div>
        <div className="interpretation-notes">
          <article><span className="note-icon note-amber"><AlertTriangle size={20}/></span><div><h3>Repair has not been demonstrated</h3><p>The rule-based and Gemini-assisted variants stopped after two rejected changes in every seed. Their strict all-targets-displaced verification rule prevented acceptance, not a proven biological impossibility.</p></div></article>
          <article><span className="note-icon"><CheckCircle2 size={20}/></span><div><h3>Recombination is a serious comparator</h3><p>It reached the eligible pool's recorded maximum in eight of ten seeds. This is promising for this finite pool, not a general claim about protein design.</p></div></article>
          <article><span className="note-icon note-amber"><AlertTriangle size={20}/></span><div><h3>The top-1% measure is saturated</h3><p>All initial sets already contained a top-1% variant. The metric cannot distinguish search policies in this experiment.</p></div></article>
        </div>
      </section>
      <aside className="provenance-panel"><div><p className="eyebrow">SOURCE OF TRUTH</p><h2>See the complete evidence.</h2><p>All displayed figures come from the committed repeated matched findings and run-summary artifacts. Historical files and source fingerprints remain available in the research branch.</p></div><a href={RESEARCH_SOURCE} target="_blank" rel="noreferrer" className="button button-dark">Open research report <ArrowUpRight size={18}/></a></aside>
      <footer className="site-footer"><span>CERA / DEVELOPMENT EVIDENCE</span><span>NO CLAIMS WITHOUT A RECORD</span><a href={RESEARCH_SOURCE} target="_blank" rel="noreferrer">Source <ArrowUpRight size={13}/></a></footer>
    </div>
  </>;
}
