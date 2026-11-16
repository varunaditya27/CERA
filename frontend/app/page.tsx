import Link from 'next/link';
import { ArrowDownRight, ArrowRight, ArrowUpRight, FlaskConical, MoveUpRight } from 'lucide-react';
import { Topbar } from '../components/topbar';
import { DATASET_REFERENCE, RESEARCH_SOURCE, SNAPSHOT_DATE } from '../lib/research';
import { getDatasets } from '../lib/datasets';

export const dynamic = 'force-dynamic';

export default async function Home() {
  const apiDatasets = await getDatasets();
  const landscapes = apiDatasets ?? DATASET_REFERENCE;
  return <>
    <Topbar section="Overview"/>
    <div className="home-content">
      <section className="hero" aria-labelledby="hero-heading">
        <div className="hero-copy">
          <p className="eyebrow eyebrow-light"><span className="eyebrow-dash"/>A RESEARCH ATLAS / NO. 001</p>
          <h1 id="hero-heading">A search that <em>questions</em> itself.</h1>
          <p className="hero-description">When learned rewards mislead protein optimization, CERA asks what broke, what can change, and what the evidence actually supports.</p>
          <div className="hero-actions">
            <Link className="button button-copper" href="/experiments">Examine the evidence <ArrowUpRight size={17} aria-hidden="true"/></Link>
            <Link className="text-action text-action-light" href="/workflow">Understand the method <ArrowRight size={16} aria-hidden="true"/></Link>
          </div>
        </div>
        <div className="hero-instrument" aria-label="Illustrative decision trace, not an experimental result">
          <div className="instrument-header"><span>DECISION TRACE</span><span>SCHEMATIC / 001</span></div>
          <div className="instrument-ruler" aria-hidden="true"><span>00</span><span>01</span><span>02</span><span>03</span><span>04</span></div>
          <div className="instrument-sequence"><span>V</span><span>A</span><span>L</span><span>G</span><span className="altered">S</span><span>N</span><span>Y</span><span>E</span><span>G</span><span>L</span><span>K</span><span>Q</span></div>
          <div className="instrument-lines">
            <div><small>MODEL EXPECTATION</small><span className="trace-line trace-predicted"/><b>HIGH</b></div>
            <div><small>MEASURED RESPONSE</small><span className="trace-line trace-observed"/><b>LOW</b></div>
            <div className="instrument-divider"/>
            <div className="instrument-finding"><span className="finding-glyph">◇</span><div><strong>Counterexample recorded</strong><small>Evidence changes what gets trusted next.</small></div></div>
          </div>
          <div className="instrument-footer"><span>ILLUSTRATIVE · NOT STUDY DATA</span><span>TRACE / VERIFY / REPEAT</span></div>
        </div>
        <div className="hero-footnote"><span>PROTEIN FITNESS OPTIMIZATION</span><span>COUNTEREXAMPLE-GUIDED REWARD AUDITING</span><ArrowDownRight size={20} strokeWidth={1.4} aria-hidden="true"/></div>
      </section>

      <section className="reading-strip" aria-label="Research snapshot">
        <div><span className="strip-label">LATEST EVIDENCE / {SNAPSHOT_DATE}</span><strong>Development, not a final biological evaluation.</strong></div>
        <div className="strip-values"><span><b>90</b> matched runs</span><span><b>09</b> search policies</span><span><b>120</b> attempted repairs</span></div>
      </section>

      <section className="editorial-section finding-section" aria-labelledby="finding-heading">
        <div className="section-margin"><span className="section-index">01 / OBSERVATION</span><span className="section-rule"/></div>
        <div className="finding-body"><p className="eyebrow">THE CURRENT FINDING</p>
          <h2 id="finding-heading">The first useful result is a <em>hard question.</em></h2>
          <p>In ten matched alpha-amylase seeds, both repair strategies stopped after repeated unsuccessful checks. No proposed reward change was accepted. Meanwhile, a finite-pool recombination baseline found the highest measured eligible score in eight of ten runs.</p>
          <div className="finding-bottom"><Link className="inline-arrow" href="/experiments">Study the comparison <MoveUpRight size={18} aria-hidden="true"/></Link><span>DEVELOPMENT RESULTS · N=10 SEEDS</span></div>
        </div>
        <div className="finding-aside"><span>IN THE RECORD</span><div className="big-figure">0<small>accepted changes</small></div><p>Rejection is a recorded outcome, not proof that repair is impossible.</p><a href={RESEARCH_SOURCE} target="_blank" rel="noreferrer">View source study <ArrowUpRight size={14}/></a></div>
      </section>

      <section className="editorial-section landscape-home" aria-labelledby="landscape-heading">
        <div className="section-margin"><span className="section-index">02 / MATERIAL</span><span className="section-rule"/></div>
        <div className="section-intro"><div><p className="eyebrow">EXPERIMENTAL LANDSCAPES</p><h2 id="landscape-heading">The evidence has <em>origins.</em></h2></div><Link className="inline-arrow" href="/datasets">Browse all datasets <MoveUpRight size={17} aria-hidden="true"/></Link></div>
        <div className="landscape-stack">
          {landscapes.slice(0,3).map((dataset,i)=><Link className="landscape-home-row" key={dataset.id} href={'/datasets/'+dataset.id}>
            <span className="landscape-ordinal">0{i+1}</span><div><h3>{dataset.name}</h3><p>{dataset.note}</p></div><span className="landscape-tag">{dataset.purpose}</span><strong>{dataset.variants?.toLocaleString('en-US') ?? '—'}</strong><ArrowUpRight size={19} aria-hidden="true"/>
          </Link>)}
        </div>
        {!apiDatasets && <p className="snapshot-disclaimer">Counts shown from the committed dataset reference snapshot. Local catalog API is offline.</p>}
      </section>

      <section className="method-teaser" aria-labelledby="method-teaser-heading">
        <div><p className="eyebrow eyebrow-light">THE CERA PROTOCOL</p><h2 id="method-teaser-heading">Not just a better score.<br/><em>A better reason.</em></h2><p>Make a prediction. Preserve what was known. Reveal the measurement. Let any proposed repair face its own evidence.</p><Link className="button button-outline" href="/workflow">Follow the method <ArrowRight size={17}/></Link></div>
        <ol className="method-mini"><li><span>01</span>Specify <small>bound the reward</small></li><li><span>02</span>Search <small>respect the budget</small></li><li><span>03</span>Audit <small>record warnings</small></li><li><span>04</span>Repair <small>verify or retain</small></li></ol>
        <FlaskConical className="method-ghost" size={152} strokeWidth={0.7} aria-hidden="true"/>
      </section>

      <footer className="site-footer"><span>CERA / RESEARCH ATLAS</span><span>TRACE THE CLAIM. KEEP THE EVIDENCE.</span><a href="https://github.com/varunaditya27/CERA" target="_blank" rel="noreferrer">GitHub <ArrowUpRight size={13}/></a></footer>
    </div>
  </>;
}
