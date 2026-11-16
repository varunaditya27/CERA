import Link from 'next/link';
import { ArrowRight, ArrowUpRight } from 'lucide-react';
import { Topbar } from '../components/topbar';
import { DATASET_REFERENCE, RESEARCH_SOURCE } from '../lib/research';
import { getDatasets } from '../lib/datasets';

export const dynamic='force-dynamic';

function SignalGraphic() {
  return <svg className="signal-graphic" viewBox="0 0 560 420" role="img" aria-label="Illustration of a model prediction diverging from an observed measurement">
    <defs><pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#71857A" strokeOpacity=".14" strokeWidth="1"/></pattern></defs>
    <rect width="560" height="420" fill="url(#grid)"/>
    <path d="M36 300H522" stroke="#73857C" strokeOpacity=".55"/><path d="M36 40V330" stroke="#73857C" strokeOpacity=".55"/>
    <path d="M45 282 C116 252 168 254 218 205 S340 119 410 104 S489 89 515 66" fill="none" stroke="#BBD4C7" strokeWidth="3.2" strokeLinecap="round"/>
    <path d="M45 282 C116 252 168 254 218 205 S302 194 341 233 S421 275 515 259" fill="none" stroke="#DA925F" strokeWidth="3.2" strokeLinecap="round"/>
    <path d="M272 165V219" stroke="#F1EDE4" strokeWidth="1.1" strokeDasharray="4 7" strokeOpacity=".68"/>
    <circle cx="272" cy="165" r="6" fill="#BBD4C7"/><circle cx="272" cy="219" r="6" fill="#DA925F"/>
    <path d="M272 189L283 200L272 211L261 200Z" fill="#DA925F" stroke="#15201D" strokeWidth="3"/>
    <text x="338" y="91" fill="#BBD4C7" fontSize="14">Prediction</text><text x="395" y="292" fill="#DA925F" fontSize="14">Observation</text>
    <text x="40" y="354" fill="#9CAEA4" fontSize="12">Illustrative, not experimental data</text>
  </svg>;
}

export default async function Home(){
  const apiDatasets=await getDatasets();
  const datasets=apiDatasets ?? DATASET_REFERENCE;
  return <><Topbar section="Overview"/><div className="home-content">
    <section className="hero">
      <div className="hero-copy">
        <h1>When the reward is wrong.</h1>
        <p>Investigating unreliable learned rewards in protein fitness optimization.</p>
        <Link href="/experiments" className="button button-accent">View results <ArrowUpRight size={17} aria-hidden="true"/></Link>
      </div>
      <div className="hero-visual"><SignalGraphic/></div>
    </section>

    <section className="summary-line" aria-label="Latest development study">
      <div><span className="quiet-label">Alpha amylase study</span><h2>90 matched runs. No accepted repairs.</h2><p>The verifier rejected all proposed reward changes. The recombination baseline reached the eligible-pool maximum in 8 of 10 seeds.</p><a className="inline-link" href={RESEARCH_SOURCE} target="_blank" rel="noreferrer">Read study <ArrowUpRight size={16} aria-hidden="true"/></a></div>
      <div className="study-figure"><strong>0<span>/120</span></strong><span>Accepted repair proposals</span></div>
    </section>

    <section className="home-datasets">
      <div className="section-head"><h2>Datasets</h2><Link href="/datasets" className="inline-link">View all <ArrowRight size={17} aria-hidden="true"/></Link></div>
      <div className="dataset-preview">
        {datasets.slice(0,3).map((dataset)=> <Link key={dataset.id} href={'/datasets/'+dataset.id} className="dataset-preview-row">
          <span className="dataset-preview-name">{dataset.name}</span><span className="dataset-preview-role">{dataset.purpose}</span>
          <span className="dataset-preview-count">{dataset.variants?.toLocaleString('en-US') ?? '—'} <small>variants</small></span>
          <ArrowUpRight size={17} aria-hidden="true"/>
        </Link>)}
      </div>
      {!apiDatasets && <p className="quiet-note">Showing committed dataset counts. API not connected.</p>}
    </section>
    <section className="home-method"><div><h2>Method</h2><p>Specify, search, audit, and verify any proposed repair.</p></div><Link href="/workflow" className="inline-link">How it works <ArrowRight size={18}/></Link></section>
    <footer className="site-footer"><span>CERA</span><a href="https://github.com/varunaditya27/CERA" target="_blank" rel="noreferrer">Source code <ArrowUpRight size={14}/></a></footer>
  </div></>;
}
