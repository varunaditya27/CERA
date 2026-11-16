import Link from 'next/link';
import { ArrowDown, ArrowRight, ArrowUpRight } from 'lucide-react';
import { HeroLandscape } from '../components/hero-landscape';
import { LandingMotion } from '../components/landing-motion';
import { SectionReveal } from '../components/section-reveal';
import { DATASET_REFERENCE, RESEARCH_SOURCE } from '../lib/research';
import { getDatasets } from '../lib/datasets';

export const dynamic='force-dynamic';

const featuredMethods=[
  {name:'Recombination',fitness:'0.21163',ratio:1},
  {name:'Random',fitness:'0.19711',ratio:0.1971083333333333/0.2116333333333333},
  {name:'CERA repair',fitness:'0.19332',ratio:0.19331666666666664/0.2116333333333333}
];

export default async function Home(){
  const api=await getDatasets();
  const datasets=api??DATASET_REFERENCE;

  return <div className="landing">
    <LandingMotion/>
    <section className="landing-hero" aria-labelledby="landing-title">
      <div className="hero-grain" aria-hidden="true"/>
      <div className="landing-hero-inner">
        <div className="landing-hero-copy">
          <h1 id="landing-title" aria-label="When the reward is wrong."><span className="hero-line"><span className="hero-line-inner">When the</span></span><span className="hero-line"><span className="hero-line-inner">reward is</span></span><span className="hero-line"><span className="hero-line-inner"><em className="hero-accent">wrong.</em></span></span></h1>
          <p>CERA investigates how to detect and correct unreliable learned rewards in protein optimization.</p>
          <div className="hero-links">
            <Link className="action-solid" href="/workflow">Explore the method <ArrowUpRight size={18} aria-hidden="true"/></Link>
            <Link className="action-text" href="/experiments">See results <ArrowRight size={18} aria-hidden="true"/></Link>
          </div>
        </div>
        <HeroLandscape/>
      </div>
      <div className="hero-bottom">
        <span>Protein fitness optimization</span>
        <a href="#question" aria-label="Scroll to the research question">Scroll to explore <ArrowDown size={16} aria-hidden="true"/></a>
      </div>
    </section>

    <section id="question" className="question-section wrap">
      <SectionReveal className="question-grid">
        <div className="chapter-index">01 <span>Research question</span></div>
        <h2>Can a search tell when its own scoring rule has failed?</h2>
        <div className="question-aside">
          <p>Prediction models can rank promising protein variants incorrectly. CERA records those failures and tests whether a constrained change to the reward improves subsequent search.</p>
          <Link href="/workflow" className="underlined-link">How CERA works <ArrowUpRight size={17}/></Link>
        </div>
      </SectionReveal>
    </section>

    <section className="process-section" aria-labelledby="process-heading">
      <div className="wrap">
        <SectionReveal>
          <div className="process-heading"><h2 id="process-heading">The process</h2><span>Four stages</span></div>
          <div className="process-rail" role="list">
            {[
              {number:'01',name:'Specify',detail:'Define a bounded reward.'},
              {number:'02',name:'Search',detail:'Select variants within budget.'},
              {number:'03',name:'Audit',detail:'Compare prediction with measurement.'},
              {number:'04',name:'Repair',detail:'Verify a change or retain the original.'}
            ].map(step=><div role="listitem" key={step.number} className="process-item">
              <span className="process-number">{step.number}</span>
              <h3>{step.name}</h3>
              <p>{step.detail}</p>
            </div>)}
          </div>
        </SectionReveal>
      </div>
    </section>

    <section className="evidence-section" aria-labelledby="evidence-heading">
      <div className="wrap">
        <SectionReveal className="evidence-grid">
          <div className="evidence-copy">
            <span className="chapter-index">02 <span>Development findings</span></span>
            <h2 id="evidence-heading">The results are not yet a success story.</h2>
            <p>Across ten matched alpha-amylase seeds, neither repair policy accepted a change. Recombination was the strongest method by median best fitness.</p>
            <Link href="/experiments" className="action-outline-light">View the comparison <ArrowUpRight size={18}/></Link>
          </div>
          <div className="evidence-plot">
            <div className="evidence-plot-head"><span>Median best fitness</span><span>Alpha amylase · 10 seeds</span></div>
            {featuredMethods.map(row=><div className="plot-row" key={row.name}>
              <div className="plot-label"><span>{row.name}</span><b>{row.fitness}</b></div>
              <div className="plot-track"><div className="plot-fill" style={{width:`${row.ratio*100}%`}}/></div>
            </div>)}
            <div className="plot-foot"><span>0</span><span>0.21163</span></div>
            <p>Scores are from a retrospective, finite pool. Higher is better.</p>
          </div>
        </SectionReveal>
      </div>
    </section>

    <section className="landscapes-section wrap" aria-labelledby="datasets-heading">
      <SectionReveal>
        <div className="section-heading"><div><span className="chapter-index">03 <span>Data</span></span><h2 id="datasets-heading">Protein landscapes</h2></div><Link className="underlined-link" href="/datasets">All datasets <ArrowUpRight size={17}/></Link></div>
        <div className="landscapes-list">
          {datasets.slice(0,3).map((dataset,i)=><Link className="landscape-entry" key={dataset.id} href={'/datasets/'+dataset.id}>
            <span className="landscape-entry-index">{String(i+1).padStart(2,'0')}</span>
            <span className="landscape-entry-title">{dataset.name}<small>{dataset.shift} shift</small></span>
            <span className="landscape-entry-role">{dataset.purpose}</span>
            <span className="landscape-entry-count">{dataset.variants?.toLocaleString('en-US')??'—'}</span>
            <ArrowUpRight size={20} aria-hidden="true"/>
          </Link>)}
        </div>
        {!api&&<p className="snapshot-note">Dataset counts from the committed research snapshot.</p>}
      </SectionReveal>
    </section>

    <footer className="landing-footer">
      <div className="wrap footer-inner"><div><span className="footer-wordmark">CERA</span><p>Counterexample-guided reward auditing</p></div>
        <div className="footer-links"><Link href="/workflow">Method</Link><Link href="/experiments">Results</Link><a href={RESEARCH_SOURCE} target="_blank" rel="noreferrer">Research source <ArrowUpRight size={15}/></a></div>
      </div>
    </footer>
  </div>;
}
