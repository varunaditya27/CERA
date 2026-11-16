import Link from 'next/link';
import { ArrowDown, ArrowRight, ArrowUpRight } from 'lucide-react';
import { HeroLandscape } from '../components/hero-landscape';
import { LandingMotion } from '../components/landing-motion';
import { SectionReveal } from '../components/section-reveal';
import { DATASET_REFERENCE, RESEARCH_SOURCE } from '../lib/research';

const featuredMethods=[
 {name:'Recombination',fitness:'0.21163',ratio:1},
 {name:'Random selection',fitness:'0.19711',ratio:0.1971083333333333/0.2116333333333333},
 {name:'Rule-based CERA',fitness:'0.19332',ratio:0.19331666666666664/0.2116333333333333},
];

export default function Home(){
 return <div className="landing">
  <LandingMotion/>
  <section className="landing-hero" aria-labelledby="landing-title">
   <div className="hero-grain" aria-hidden="true"/>
   <div className="landing-hero-inner">
    <div className="landing-hero-copy">
     <p className="hero-identifier">CERA / PROTEIN FITNESS RESEARCH</p>
     <h1 id="landing-title">
      <span className="hero-line"><span className="hero-line-inner">A prediction</span></span>
      <span className="hero-line"><span className="hero-line-inner">isn't <span className="hero-accent">proof.</span></span></span>
     </h1>
     <p>What happens when a protein search trusts the wrong score? CERA investigates how to spot the mismatch and test a correction.</p>
     <div className="hero-links">
      <Link className="action-solid" href="/walkthrough">Try the walkthrough <ArrowUpRight size={18} aria-hidden="true"/></Link>
      <Link className="action-text" href="/experiments">View results <ArrowRight size={18} aria-hidden="true"/></Link>
     </div>
    </div>
    <div className="hero-display" aria-label="Conceptual example: a score of 9 was predicted and a score of 3 was measured">
     <HeroLandscape/>
     <div className="hero-readout hero-readout-forecast"><span>Model prediction</span><strong>9</strong></div>
     <div className="hero-readout hero-readout-observed"><span>Actual measurement</span><strong>3</strong></div>
     <span className="hero-display-note">Illustrative values</span>
    </div>
   </div>
   <div className="hero-bottom"><span>Protein fitness research</span><a href="#question" aria-label="Scroll to the research question">Explore <ArrowDown size={16} aria-hidden="true"/></a></div>
  </section>

  <section id="question" className="question-section wrap">
   <SectionReveal className="question-grid">
    <span className="chapter-index">01 <span>The question</span></span>
    <h2>A high predicted score doesn't always mean a good protein.</h2>
    <div className="question-aside">
     <p>The search chooses which protein variants to measure. When the prediction and measurement disagree, that contradiction becomes evidence for the next decision.</p>
     <Link href="/walkthrough" className="underlined-link">See an example <ArrowUpRight size={17}/></Link>
    </div>
   </SectionReveal>
  </section>

  <section className="home-example" aria-labelledby="example-heading">
   <div className="wrap home-example-grid">
    <SectionReveal className="home-example-copy">
     <span className="chapter-index">02 <span>What the search can see</span></span>
     <h2 id="example-heading">The next score is still <span>hidden.</span></h2>
     <p>Protein sequences are visible, but unmeasured fitness scores are not. The system must choose what to measure before seeing the answer.</p>
     <Link className="underlined-link" href="/walkthrough">Try the selection <ArrowUpRight size={17}/></Link>
    </SectionReveal>
    <div className="home-example-figure" aria-label="Illustrative starting view with two known protein scores and four hidden ones">
     <div className="visibility-head"><span>Protein</span><span>Measured fitness</span></div>
     <div className="visibility-grid">
      {[
       {id:'A',score:'4',known:true},{id:'B',score:'6',known:true},
       {id:'C',score:'?',known:false},{id:'D',score:'?',known:false},
       {id:'E',score:'?',known:false},{id:'F',score:'?',known:false},
      ].map(item=><div key={item.id} className={item.known?'visibility-cell is-known':'visibility-cell'}>
       <span>{item.id}</span><strong>{item.score}</strong><small>{item.known?'Measured':'Hidden'}</small>
      </div>)}
     </div>
     <p className="case-caption">Illustrative starting set, not experimental data</p>
    </div>
   </div>
  </section>

  <section className="process-section" aria-labelledby="process-heading">
   <div className="wrap">
    <SectionReveal>
     <div className="process-heading"><h2 id="process-heading">How CERA works</h2><Link href="/workflow" className="underlined-link">Full method <ArrowUpRight size={17}/></Link></div>
     <div className="process-rail" role="list">
      {[
       {number:'01',name:'Specify',detail:'Set the goal and hard limits.'},
       {number:'02',name:'Search',detail:'Choose which variants to measure.'},
       {number:'03',name:'Audit',detail:'Check where the model disagreed.'},
       {number:'04',name:'Repair',detail:'Test a change before accepting it.'}
      ].map(step=><div role="listitem" key={step.number} className="process-item">
       <span className="process-number">{step.number}</span><h3>{step.name}</h3><p>{step.detail}</p>
      </div>)}
     </div>
    </SectionReveal>
   </div>
  </section>

  <section className="evidence-section" aria-labelledby="evidence-heading">
   <div className="wrap">
    <SectionReveal className="evidence-grid">
     <div className="evidence-copy">
      <span className="chapter-index">03 <span>Development results</span></span>
      <h2 id="evidence-heading">The first repairs didn't pass.</h2>
      <p>Across 90 matched amylase runs, neither repair policy accepted a change. Recombination performed best by median observed fitness.</p>
      <Link href="/experiments" className="action-outline-light">Compare methods <ArrowUpRight size={18}/></Link>
     </div>
     <div className="evidence-plot">
      <div className="evidence-plot-head"><span>Median best fitness</span><span>Alpha amylase / 10 seeds</span></div>
      {featuredMethods.map(row=><div className="plot-row" key={row.name}>
       <div className="plot-label"><span>{row.name}</span><b>{row.fitness}</b></div>
       <div className="plot-track"><div className="plot-fill" style={{width:`${row.ratio*100}%`}}/></div>
      </div>)}
      <div className="plot-foot"><span>0</span><span>0.21163</span></div>
      <p>Development results on one protein. Higher fitness is better.</p>
     </div>
    </SectionReveal>
   </div>
  </section>

  <section className="landscapes-section wrap" aria-labelledby="datasets-heading">
   <SectionReveal>
    <div className="section-heading">
     <div><span className="chapter-index">04 <span>Datasets</span></span><h2 id="datasets-heading">Three protein landscapes.</h2></div>
     <Link className="underlined-link" href="/datasets">All datasets <ArrowUpRight size={17}/></Link>
    </div>
    <div className="landscapes-list">
     {DATASET_REFERENCE.slice(0,3).map((dataset,i)=><Link className="landscape-entry" key={dataset.id} href={'/datasets/'+dataset.id}>
      <span className="landscape-entry-index">{String(i+1).padStart(2,'0')}</span>
      <span className="landscape-entry-title">{dataset.name}<small>{dataset.shift} shift</small></span>
      <span className="landscape-entry-role">{i===0?'Development':'Testing pending'}</span>
      <span className="landscape-entry-count">{dataset.variants?.toLocaleString('en-US')??'—'}</span>
      <ArrowUpRight size={20} aria-hidden="true"/>
     </Link>)}
    </div>
    <p className="snapshot-note">Counts from the committed research snapshot.</p>
   </SectionReveal>
  </section>

  <section className="home-endnote"><div className="wrap home-endnote-grid"><div><h2>Inside the system.</h2><p>The experiment runner, model, and repair checks are separate from this website.</p></div><Link className="underlined-link" href="/system">See what's built <ArrowUpRight size={17}/></Link></div></section>

  <footer className="landing-footer"><div className="wrap footer-inner">
   <div><span className="footer-wordmark">CERA</span><p>Counterexample-guided reward auditing</p></div>
   <div className="footer-links"><Link href="/walkthrough">Walkthrough</Link><Link href="/workflow">Method</Link><Link href="/experiments">Results</Link><a href={RESEARCH_SOURCE} target="_blank" rel="noreferrer">Study <ArrowUpRight size={15}/></a></div>
  </div></footer>
 </div>;
}
